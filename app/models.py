# app/models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relación si la requieres, por ejemplo, con productos
    # productos = relationship("Producto", back_populates="categoria")


class Editorial(Base):
    __tablename__ = "editorial"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # productos = relationship("Producto", back_populates="editorial")


class Producto(Base):
    __tablename__ = "productos"

    id_producto = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(255), nullable=False)
    stock_actual = Column(Integer, default=0)
    imagen_url = Column(String(255))
    precio_proveedor = Column(Float)
    precio = Column(Float)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())
    categorias_id = Column(Integer, ForeignKey("categorias.id"))
    editorial_id = Column(Integer, ForeignKey("editorial.id"))

    # Relaciones
    # categoria = relationship("Categoria", back_populates="productos")
    # editorial = relationship("Editorial", back_populates="productos")
