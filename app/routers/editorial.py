# app/routers/editorial.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app import schemas

router = APIRouter(
    prefix="/editorials",
    tags=["Ver todas las editoriales"]
)

@router.get("/", response_model=list[schemas.Editorial])
async def get_editorials(db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM editorial")
    result = await db.execute(query)
    rows = result.fetchall()
    
    editoriales = []
    for row in rows:
        editorial_dict = {
            "id": row.id,
            "nombre": row.nombre,
            "fecha_creacion": row.fecha_creacion,
            "fecha_actualizacion": row.fecha_actualizacion,
        }
        editoriales.append(schemas.Editorial(**editorial_dict))
        
    return editoriales
