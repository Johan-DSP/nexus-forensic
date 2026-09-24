"""
Fixtures globales de la suite de tests de NEXUS Forensic.

IMPORTANTE: las variables de entorno se configuran ANTES de importar
cualquier módulo de `app` para que `Settings` las lea correctamente.
Cada sesión de pytest usa su propia DB temporal y su propio storage.
"""

import os
import shutil
import tempfile
from pathlib import Path

# -----------------------------------------------------------------
# Entorno aislado — ANTES de importar `app.*`
# -----------------------------------------------------------------
_TMPDIR = Path(tempfile.mkdtemp(prefix="nexus_test_"))
os.environ["DATABASE_URL"] = f"sqlite:///{_TMPDIR / 'test.db'}"
os.environ["STORAGE_PATH"] = str(_TMPDIR / "storage")
os.environ["CORS_ORIGINS"] = '["http://testserver"]'
os.environ["APP_ENV"] = "test"


# -----------------------------------------------------------------
# Imports (post-configuración de entorno)
# -----------------------------------------------------------------
import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.database import SessionLocal, engine, get_db
from app.main import app


# -----------------------------------------------------------------
# Override de get_db para que use la DB de test
# -----------------------------------------------------------------
def _override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


# -----------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------
@pytest.fixture(autouse=True)
def _reset_db():
    """Recrea todas las tablas antes y después de cada test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Cliente HTTP con el override ya aplicado."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session():
    """Sesión directa a la DB para aserciones a bajo nivel."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_case(client):
    """Caso base para tests que necesitan un caso ya creado."""
    resp = client.post(
        "/api/cases/",
        json={
            "case_number": "TEST-001",
            "title": "Caso de prueba",
            "description": "Caso creado por pytest",
            "status": "OPEN",
        },
    )
    assert resp.status_code == 201
    return resp.json()


def pytest_sessionfinish(session, exitstatus):  # noqa: ARG001
    """Limpia el directorio temporal al terminar la sesión completa."""
    shutil.rmtree(_TMPDIR, ignore_errors=True)
