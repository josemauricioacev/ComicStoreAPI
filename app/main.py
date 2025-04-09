# app/main.py

from fastapi import FastAPI
from app.routers import categories, editorial, recommendations

app = FastAPI(
    title="ComicStore API",
    version="1.0.0",
    description="API para gestionar y recomendar comics."
)

# Incluir routers
app.include_router(categories.router)
app.include_router(editorial.router)
app.include_router(recommendations.router)

@app.get("/")
def root():
    return {"message": "¡Bienvenido a ComicStore API! Visita /docs para ver la magia."}
