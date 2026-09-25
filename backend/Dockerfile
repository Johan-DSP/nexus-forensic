FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

# curl para el healthcheck del compose
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# 1. Dependencias
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 2. Código de la aplicación
COPY backend/app ./app

# 3. Alembic (config + migraciones)
COPY backend/alembic.ini ./alembic.ini
COPY backend/alembic ./alembic

# 4. Scripts (seed, etc.)
COPY scripts ./scripts

EXPOSE 8000

# Alembic aplica migraciones pendientes y luego arranca uvicorn
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
