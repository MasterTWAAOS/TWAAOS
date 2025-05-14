from logging.config import fileConfig
import asyncio
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import models package which loads all models and their metadata
import models
from models.base import Base
from config.database import SQLALCHEMY_DATABASE_URL

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with the URL from our application
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    # Convert async URL to sync URL for offline mode
    if url.startswith("postgresql+asyncpg"):
        url = url.replace("postgresql+asyncpg", "postgresql")
        
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Better for SQLite but works with Postgres too
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode using async SQLAlchemy.

    In this scenario we need to create an AsyncEngine
    and associate a connection with the context.
    """
    # Create a sync function for Alembic to run
    def do_migrations(connection: Connection) -> None:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

    # Create async engine
    async def run_async_migrations() -> None:
        config_section = config.get_section(config.config_ini_section)
        
        # Use async_engine_from_config instead of engine_from_config
        connectable = async_engine_from_config(
            config_section,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        async with connectable.connect() as connection:
            await connection.run_sync(do_migrations)
        
        # Close the engine connection
        await connectable.dispose()
    
    # Run the async function in the asyncio event loop
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()