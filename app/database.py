# app/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del .env

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# URI para MySQL Async con aiomysql, por ejemplo:
DATABASE_URL = (
    f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Crea el engine asíncrono
engine = create_async_engine(DATABASE_URL, echo=False)

# Crea una factoría de sesiones
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    """Dependencia para obtener la sesión de la BD."""
    async with async_session() as session:
        yield session
