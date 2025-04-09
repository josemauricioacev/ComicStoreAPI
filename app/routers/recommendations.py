from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app import schemas  # <--- Importamos el schemas


router = APIRouter(
    prefix="/recommendations"
)

@router.get(
    "/bestseller",
    response_model=schemas.ComicRecommendation,
    tags=["Cómics más vendidos"],
    summary="Obtener el cómic más vendido",
    description="""
    Retorna el cómic con la mayor cantidad de ventas registradas.

    - Realiza una consulta sobre la tabla `detallespedidos` para contar cuántas unidades se han vendido por producto.
    - Utiliza `GROUP BY` y `SUM(cantidad)` para calcular el total de ventas por cómic.
    - Ordena los resultados de mayor a menor y limita la salida a 1 resultado.
    """
)
async def get_bestseller_comic(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT p.id_producto, 
               p.descripcion, 
               p.precio, 
               c.nombre AS categoria, 
               e.nombre AS editorial,
               SUM(d.cantidad) AS total_vendido
        FROM productos p
        JOIN detallespedidos d ON p.id_producto = d.id_producto
        JOIN categorias c ON p.categorias_id = c.id
        JOIN editorial e ON p.editorial_id = e.id
        GROUP BY p.id_producto, p.descripcion, p.precio, c.nombre, e.nombre
        ORDER BY total_vendido DESC
        LIMIT 1
    """)

    result = await db.execute(query)
    row = result.first()
    if row:
        return schemas.ComicRecommendation(
            id_producto=row.id_producto,
            descripcion=row.descripcion,
            precio=row.precio,
            categoria=row.categoria,
            editorial=row.editorial,
            total_vendido=int(row.total_vendido)
        )
    else:
        raise HTTPException(status_code=404, detail="No se encontró comic bestseller")



@router.get(
    "/worst",
    response_model=schemas.ComicRecommendation,
    tags=["Cómics menos vendidos"],
    summary="Obtener el cómic menos vendido",
    description="""
    Retorna el cómic con la menor cantidad de ventas registradas en la base de datos.

    - Utiliza un `LEFT JOIN` con la tabla `detallespedidos` para incluir también cómics que nunca se han vendido.
    - Agrupa por ID del producto y obtiene el cómic con menor cantidad total vendida.
    """
)
async def get_worst_selling_comic(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT p.id_producto, 
               p.descripcion, 
               p.precio, 
               c.nombre AS categoria, 
               e.nombre AS editorial,
               COALESCE(SUM(d.cantidad), 0) AS total_vendido
        FROM productos p
        LEFT JOIN detallespedidos d ON p.id_producto = d.id_producto
        JOIN categorias c ON p.categorias_id = c.id
        JOIN editorial e ON p.editorial_id = e.id
        GROUP BY p.id_producto, p.descripcion, p.precio, c.nombre, e.nombre
        ORDER BY total_vendido ASC
        LIMIT 1
    """)
    
    result = await db.execute(query)
    row = result.first()
    if row:
        return schemas.ComicRecommendation(
            id_producto=row.id_producto,
            descripcion=row.descripcion,
            precio=row.precio,
            categoria=row.categoria,
            editorial=row.editorial,
            total_vendido=int(row.total_vendido)
        )
    else:
        raise HTTPException(status_code=404, detail="No se encontró comic con bajas ventas")



@router.get(
    "/recent",
    response_model=list[schemas.ComicRecent],
    tags=["Cómics recientes"],
    summary="Listar cómics recientemente agregados",
    description="""
    Devuelve los 5 cómics más recientes registrados en la base de datos.

    - Se unen las tablas `productos`, `categorias` y `editorial` para obtener la información completa del cómic.
    - Se ordenan en orden descendente por la fecha de registro.
    """
)
async def get_recent_comics(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT p.id_producto,
               p.descripcion,
               p.precio,
               c.nombre AS categoria,
               e.nombre AS editorial,
               p.fecha_registro
        FROM productos p
        JOIN categorias c ON p.categorias_id = c.id
        JOIN editorial e ON p.editorial_id = e.id
        ORDER BY p.fecha_registro DESC
        LIMIT 5
    """)
    
    result = await db.execute(query)
    rows = result.fetchall()
    if rows:
        return [
            schemas.ComicRecent(
                id_producto=row.id_producto,
                descripcion=row.descripcion,
                precio=row.precio,
                categoria=row.categoria,
                editorial=row.editorial,
                fecha_registro=row.fecha_registro
            )
            for row in rows
        ]
    else:
        raise HTTPException(status_code=404, detail="No se encontraron comics recientemente agregados")




@router.get(
    "/discounts",
    response_model=list[schemas.ComicDiscount],
    tags=["Descuentos activos"],
    summary="Obtener cómics en descuento",
    description="""
    Retorna una lista de cómics que actualmente están en promoción.

    - Solo se incluyen los descuentos cuya fecha actual esté entre `fecha_inicio` y `fecha_fin`.
    - Muestra detalles del producto, categoría, editorial y descripción del descuento.
    - Ordenado por la fecha de inicio del descuento.
    """
)
async def get_discounted_comics(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT p.id_producto,
               p.descripcion,
               p.precio,
               c.nombre AS categoria,
               e.nombre AS editorial,
               d.descripcion AS descuento_descripcion,
               d.fecha_inicio,
               d.fecha_fin
        FROM productos p
        JOIN descuentos d ON p.id_producto = d.productos_id_producto
        JOIN categorias c ON p.categorias_id = c.id
        JOIN editorial e ON p.editorial_id = e.id
        WHERE NOW() BETWEEN d.fecha_inicio AND d.fecha_fin
        ORDER BY d.fecha_inicio ASC
    """)
    
    result = await db.execute(query)
    rows = result.fetchall()
    if rows:
        return [
            schemas.ComicDiscount(
                id_producto=row.id_producto,
                descripcion=row.descripcion,
                precio=row.precio,
                categoria=row.categoria,
                editorial=row.editorial,
                descuento_descripcion=row.descuento_descripcion,
                fecha_inicio=row.fecha_inicio,
                fecha_fin=row.fecha_fin
            )
            for row in rows
        ]
    else:
        raise HTTPException(status_code=404, detail="No hay productos en descuento")

    
@router.get(
    "/by-price-range",
    response_model=list[schemas.ComicRecent],
    tags=["Filtros de precio"],
    summary="Buscar cómics por rango de precio",
    description="""
    Retorna una lista de cómics cuyo precio se encuentra entre los valores `min` y `max`.

    - Ordenado de forma ascendente por precio.
    - Incluye datos de categoría y editorial.
    - Ideal para que los clientes encuentren cómics dentro de su presupuesto.
    """
)
async def get_comics_by_price_range(min: float, max: float, db: AsyncSession = Depends(get_db)):
    if min > max:
        raise HTTPException(status_code=400, detail="El precio mínimo no puede ser mayor al máximo.")

    query = text("""
        SELECT p.id_producto,
               p.descripcion,
               p.precio,
               c.nombre AS categoria,
               e.nombre AS editorial,
               p.fecha_registro
        FROM productos p
        JOIN categorias c ON p.categorias_id = c.id
        JOIN editorial e ON p.editorial_id = e.id
        WHERE p.precio BETWEEN :min AND :max
        ORDER BY p.precio ASC
    """)
    
    result = await db.execute(query, {"min": min, "max": max})
    rows = result.fetchall()
    
    if not rows:
        raise HTTPException(status_code=404, detail="No se encontraron cómics en ese rango de precio")

    return [
        schemas.ComicRecent(
            id_producto=row.id_producto,
            descripcion=row.descripcion,
            precio=row.precio,
            categoria=row.categoria,
            editorial=row.editorial,
            fecha_registro=row.fecha_registro
        )
        for row in rows
    ]



@router.get(
    "/by-price-range",
    response_model=list[schemas.ComicRecent],
    tags=["Filtros de precio"],
    summary="Buscar cómics por rango de precio",
    description="""
    Permite filtrar cómics cuyo precio esté entre dos valores (`min` y `max`).
    Muestra la información básica del cómic, incluyendo su categoría y editorial,
    ordenando los resultados del más barato al más caro.
    """
)
async def get_comics_by_price_range(min: float, max: float, db: AsyncSession = Depends(get_db)):
    if min > max:
        raise HTTPException(status_code=400, detail="El precio mínimo no puede ser mayor al máximo.")

    query = text("""
        SELECT p.id_producto,
               p.descripcion,
               p.precio,
               c.nombre AS categoria,
               e.nombre AS editorial,
               p.fecha_registro
        FROM productos p
        JOIN categorias c ON p.categorias_id = c.id
        JOIN editorial e ON p.editorial_id = e.id
        WHERE p.precio BETWEEN :min AND :max
        ORDER BY p.precio ASC
    """)
    
    result = await db.execute(query, {"min": min, "max": max})
    rows = result.fetchall()
    
    if not rows:
        raise HTTPException(status_code=404, detail="No se encontraron cómics en ese rango de precio")

    return [
        schemas.ComicRecent(
            id_producto=row.id_producto,
            descripcion=row.descripcion,
            precio=row.precio,
            categoria=row.categoria,
            editorial=row.editorial,
            fecha_registro=row.fecha_registro
        )
        for row in rows
    ]



@router.get(
    "/bestseller-of-month",
    response_model=schemas.ComicRecommendation,
    tags=["Recomendaciones"],
    summary="Cómic más vendido del mes",
    description="Obtiene el cómic con más unidades vendidas en el mes actual. Considera las ventas registradas y agrupa los resultados para determinar el bestseller mensual."
)
async def get_bestseller_of_month(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT p.id_producto, 
               p.descripcion, 
               p.precio, 
               c.nombre AS categoria, 
               e.nombre AS editorial,
               SUM(d.cantidad) AS total_vendido
        FROM productos p
        JOIN detallespedidos d ON p.id_producto = d.id_producto
        JOIN ventas v ON d.ventas_id = v.id
        JOIN categorias c ON p.categorias_id = c.id
        JOIN editorial e ON p.editorial_id = e.id
        WHERE MONTH(v.fecha_creacion) = MONTH(NOW()) AND YEAR(v.fecha_creacion) = YEAR(NOW())
        GROUP BY p.id_producto, p.descripcion, p.precio, c.nombre, e.nombre
        ORDER BY total_vendido DESC
        LIMIT 1
    """)

    result = await db.execute(query)
    row = result.first()

    if row:
        return schemas.ComicRecommendation(
            id_producto=row.id_producto,
            descripcion=row.descripcion,
            precio=row.precio,
            categoria=row.categoria,
            editorial=row.editorial,
            total_vendido=int(row.total_vendido)
        )
    else:
        raise HTTPException(status_code=404, detail="No se encontraron ventas este mes.")




@router.get(
    "/categories-with-most-sales",
    tags=["Categorías"],
    summary="Categorías con más ventas",
    description="Lista las categorías de cómics ordenadas por la cantidad total de ventas realizadas, desde la más vendida hasta la menos vendida."
)
async def get_categories_with_most_sales(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT c.nombre AS categoria, 
               SUM(d.cantidad) AS total_vendido
        FROM categorias c
        JOIN productos p ON p.categorias_id = c.id
        JOIN detallespedidos d ON p.id_producto = d.id_producto
        GROUP BY c.nombre
        ORDER BY total_vendido DESC
    """)
    
    result = await db.execute(query)
    rows = result.fetchall()

    if rows:
        return [{"categoria": row.categoria, "total_vendido": int(row.total_vendido)} for row in rows]
    else:
        raise HTTPException(status_code=404, detail="No se encontraron ventas por categoría.")




@router.get(
    "/top-client-of-month",
    response_model=dict,
    tags=["Clientes"],
    summary="Cliente del mes",
    description="Retorna al cliente con más compras registradas en el mes actual. Muestra su ID, nombre completo, correo y total de compras realizadas."
)
async def get_top_client_of_month(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT c.id_cliente,
               c.nombre,
               c.apellido,
               c.correo,
               COUNT(v.id) AS total_compras
        FROM clientes c
        JOIN ventas v ON c.id_cliente = v.cliente_id
        WHERE MONTH(v.fecha_creacion) = MONTH(NOW()) AND YEAR(v.fecha_creacion) = YEAR(NOW())
        GROUP BY c.id_cliente, c.nombre, c.apellido, c.correo
        ORDER BY total_compras DESC
        LIMIT 1
    """)

    result = await db.execute(query)
    row = result.first()

    if row:
        return {
            "id_cliente": row.id_cliente,
            "nombre": row.nombre,
            "apellido": row.apellido,
            "correo": row.correo,
            "total_compras": int(row.total_compras)
        }
    else:
        raise HTTPException(status_code=404, detail="No se encontró cliente del mes.")




@router.get(
    "/comics-per-editorial",
    response_model=list[dict],
    tags=["Editoriales"],
    summary="Cómics agrupados por editorial",
    description="Devuelve una lista de editoriales con el total de cómics registrados en cada una, junto con los títulos de sus cómics. Útil para analizar la diversidad de productos por editorial."
)
async def get_comics_per_editorial(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT e.nombre AS editorial, p.descripcion AS comic
        FROM editorial e
        JOIN productos p ON p.editorial_id = e.id
        ORDER BY e.nombre
    """)

    result = await db.execute(query)
    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No hay cómics registrados por editorial.")

    editorial_map = {}

    for row in rows:
        ed_name = row.editorial
        if ed_name not in editorial_map:
            editorial_map[ed_name] = {
                "editorial": ed_name,
                "total_comics": 0,
                "comics": []
            }
        editorial_map[ed_name]["total_comics"] += 1
        editorial_map[ed_name]["comics"].append(row.comic)

    return list(editorial_map.values())





@router.get(
    "/most-purchased-editorial",
    response_model=dict,
    tags=["Editoriales"],
    summary="Editorial con más ventas",
    description="Retorna la editorial cuyos cómics acumulan la mayor cantidad de ventas. Ideal para conocer cuál editorial domina el mercado en tu tienda."
)
async def get_most_purchased_editorial(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT e.nombre AS editorial, SUM(d.cantidad) AS total_vendido
        FROM productos p
        JOIN editorial e ON p.editorial_id = e.id
        JOIN detallespedidos d ON p.id_producto = d.id_producto
        GROUP BY e.nombre
        ORDER BY total_vendido DESC
        LIMIT 1
    """)
    
    result = await db.execute(query)
    row = result.first()

    if row:
        return {"editorial": row.editorial, "total_vendido": int(row.total_vendido)}
    else:
        raise HTTPException(status_code=404, detail="No se encontraron ventas de cómics por editorial.")





@router.get(
    "/never-sold",
    response_model=list[dict],
    tags=["Ventas de Cómics"],
    summary="Cómics que nunca se han vendido",
    description="Devuelve una lista de cómics que no tienen registros de venta. Útil para detectar productos con baja rotación o sin demanda."
)
async def get_comics_never_sold(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT p.id_producto, p.descripcion, p.precio
        FROM productos p
        LEFT JOIN detallespedidos d ON p.id_producto = d.id_producto
        WHERE d.id_producto IS NULL
    """)

    result = await db.execute(query)
    rows = result.fetchall()

    if rows:
        return [
            {"id_producto": row.id_producto, "descripcion": row.descripcion, "precio": row.precio}
            for row in rows
        ]
    else:
        raise HTTPException(status_code=404, detail="Todos los cómics han tenido al menos una venta.")




@router.get(
    "/comics-with-stock-between",
    response_model=list[schemas.ComicRecent],
    tags=["Stock de Cómics"],
    summary="Cómics por rango de stock",
    description="Devuelve una lista de cómics cuyo stock actual se encuentra entre los valores proporcionados. Útil para filtrar productos según disponibilidad."
)
async def get_comics_by_stock_range(min: int, max: int, db: AsyncSession = Depends(get_db)):
    if min > max:
        raise HTTPException(status_code=400, detail="El stock mínimo no puede ser mayor al máximo.")

    query = text("""
        SELECT p.id_producto,
               p.descripcion,
               p.precio,
               c.nombre AS categoria,
               e.nombre AS editorial,
               p.fecha_registro
        FROM productos p
        JOIN categorias c ON p.categorias_id = c.id
        JOIN editorial e ON p.editorial_id = e.id
        WHERE p.stock_actual BETWEEN :min AND :max
        ORDER BY p.stock_actual ASC
    """)
    
    result = await db.execute(query, {"min": min, "max": max})
    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No se encontraron cómics dentro del rango de stock.")

    return [
        schemas.ComicRecent(
            id_producto=row.id_producto,
            descripcion=row.descripcion,
            precio=row.precio,
            categoria=row.categoria,
            editorial=row.editorial,
            fecha_registro=row.fecha_registro
        )
        for row in rows
    ]



@router.get(
    "/cheapest-comics",
    response_model=list[schemas.ComicRecent],
    tags=["Precios de Cómics"],
    summary="Cómics más baratos",
    description="Devuelve una lista de cómics ordenados desde el más barato hasta el más caro. Ideal para encontrar promociones, productos accesibles o ajustar precios."
)
async def get_cheapest_comics(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT p.id_producto,
               p.descripcion,
               p.precio,
               c.nombre AS categoria,
               e.nombre AS editorial,
               p.fecha_registro
        FROM productos p
        JOIN categorias c ON p.categorias_id = c.id
        JOIN editorial e ON p.editorial_id = e.id
        ORDER BY p.precio ASC
    """)
    result = await db.execute(query)
    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No hay cómics en la base de datos.")

    return [
        schemas.ComicRecent(
            id_producto=row.id_producto,
            descripcion=row.descripcion,
            precio=row.precio,
            categoria=row.categoria,
            editorial=row.editorial,
            fecha_registro=row.fecha_registro
        )
        for row in rows
    ]



@router.get(
    "/most-expensive-comics",
    response_model=list[schemas.ComicRecent],
    tags=["Precios de Cómics"],
    summary="Cómics más caros",
    description="Devuelve una lista de cómics ordenados desde el más caro hasta el más barato. Ideal para destacar productos premium o revisar el top de precios."
)
async def get_most_expensive_comics(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT p.id_producto,
               p.descripcion,
               p.precio,
               c.nombre AS categoria,
               e.nombre AS editorial,
               p.fecha_registro
        FROM productos p
        JOIN categorias c ON p.categorias_id = c.id
        JOIN editorial e ON p.editorial_id = e.id
        ORDER BY p.precio DESC
    """)
    result = await db.execute(query)
    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No hay cómics en la base de datos.")

    return [
        schemas.ComicRecent(
            id_producto=row.id_producto,
            descripcion=row.descripcion,
            precio=row.precio,
            categoria=row.categoria,
            editorial=row.editorial,
            fecha_registro=row.fecha_registro
        )
        for row in rows
    ]




@router.get(
    "/stock-alerts",
    response_model=list[schemas.ComicRecent],
    tags=["Alertas de Stock"],
    summary="Cómics con stock bajo",
    description="Devuelve una lista de cómics cuyo stock actual es menor a 5 unidades. Ideal para control de inventario."
)
async def get_low_stock_comics(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT p.id_producto,
               p.descripcion,
               p.precio,
               c.nombre AS categoria,
               e.nombre AS editorial,
               p.fecha_registro
        FROM productos p
        JOIN categorias c ON p.categorias_id = c.id
        JOIN editorial e ON p.editorial_id = e.id
        WHERE p.stock_actual < 5
        ORDER BY p.stock_actual ASC
    """)
    result = await db.execute(query)
    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No hay cómics con stock bajo.")

    return [
        schemas.ComicRecent(
            id_producto=row.id_producto,
            descripcion=row.descripcion,
            precio=row.precio,
            categoria=row.categoria,
            editorial=row.editorial,
            fecha_registro=row.fecha_registro
        )
        for row in rows
    ]
