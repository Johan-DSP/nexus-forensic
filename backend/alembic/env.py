from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# -----------------------------------------------------------------
# Hacemos visible el paquete `app` (backend/)
# -----------------------------------------------------------------
import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND_DIR))

# -----------------------------------------------------------------
# Importar Base + TODOS los modelos para que autogenerate los vea
# -----------------------------------------------------------------
from app.core.config import settings
from app.db.base import Base
from app.db.models import case, chrono, evidentia, nexus  # noqa: F401

# Metadata de SQLAlchemy para autogenerate
target_metadata = Base.metadata

# Config de Alembic
config = context.config

# Fuente de la URL: settings (respeta DATABASE_URL de .env o del entorno)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """Modo offline: genera SQL sin conectar a la DB."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # necesario para SQLite (ALTER TABLE limitado)
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Modo online: conecta a la DB y aplica las migraciones."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # SQLite: usar batch_alter_table
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
