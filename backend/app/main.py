from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

# Importar modelos ANTES de create_all
from app.db.models import case, nexus, chrono, evidentia  # noqa: F401

# Importar rutas
from app.api import (
    cases,
    nexus as nexus_api,
    chrono as chrono_api,
    evidentia as evidentia_api,
)

# Para el MVP, creamos las tablas automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Plataforma modular de apoyo al análisis de investigaciones",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(cases.router)
app.include_router(nexus_api.router)
app.include_router(chrono_api.router)
app.include_router(evidentia_api.router)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
    }
