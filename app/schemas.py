# app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CategoriaBase(BaseModel):
    nombre: str

class CategoriaCreate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        # Para Pydantic v2, en lugar de orm_mode, usa from_attributes
        from_attributes = True


class EditorialBase(BaseModel):
    nombre: str

class EditorialCreate(EditorialBase):
    pass

class Editorial(EditorialBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        orm_mode = True


class ProductoBase(BaseModel):
    descripcion: str
    precio: float

class ProductoCreate(ProductoBase):
    pass

class Producto(ProductoBase):
    id_producto: int
    fecha_registro: datetime
    fecha_actualizacion: datetime
    categorias_id: int
    editorial_id: int

    class Config:
        orm_mode = True


class ComicRecommendation(BaseModel):
    id_producto: int
    descripcion: str
    precio: float
    categoria: str
    editorial: str
    total_vendido: int

    class Config:
        # Si estás en Pydantic v2, utiliza from_attributes; en v1, usa orm_mode
        orm_mode = True  # O, en v2: from_attributes = True

class ComicRecent(BaseModel):
    id_producto: int
    descripcion: str
    precio: float
    categoria: str
    editorial: str
    fecha_registro: datetime

    class Config:
        # Usa orm_mode si estás en Pydantic v1 o from_attributes para Pydantic v2
        orm_mode = True  # O en v2: from_attributes = True

class ComicDiscount(BaseModel):
    id_producto: int
    descripcion: str
    precio: float
    categoria: str
    editorial: str
    descuento_descripcion: str
    fecha_inicio: datetime
    fecha_fin: datetime

    class Config:
        orm_mode = True  # O, en Pydantic v2: from_attributes = True