"""Alembic env - sync migrations with psycopg2."""
from logging.config import fileConfig

from sqlalchemy.engine import Connection
from alembic import context

from app.core.config import settings
from app.core.database import Base
from app.models import Agent, Post, Comment, Vote  # noqa: F401 - register models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# set sqlalchemy.url from app settings (sync URL for migrations - psycopg2)
_sync_url = settings.database_url.replace("postgresql+asyncpg", "postgresql")
config.set_main_option("sqlalchemy.url", _sync_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()




def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = config.get_main_option("sqlalchemy.url")
    from sqlalchemy import create_engine
    engine = create_engine(connectable)
    with engine.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
