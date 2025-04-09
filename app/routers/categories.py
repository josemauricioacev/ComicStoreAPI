# app/routers/categories.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app import schemas

router = APIRouter(
    prefix="/categories",
    tags=["Ver todas las categorias"]
)

@router.get("/", response_model=list[schemas.Categoria])
async def get_categories(db: AsyncSession = Depends(get_db)):
    # Consulta cruda
    query = text("SELECT * FROM categorias")
    result = await db.execute(query)
    rows = result.fetchall()  # retorna filas, no objetos 'models.Categoria'

    # Construimos la lista de Categoría "a mano" usando Pydantic
    categorias = []
    for row in rows:
        cat_dict = {
            "id": row.id,
            "nombre": row.nombre,
            "fecha_creacion": row.fecha_creacion,
            "fecha_actualizacion": row.fecha_actualizacion
        }
        categorias.append(schemas.Categoria(**cat_dict))
    return categorias
