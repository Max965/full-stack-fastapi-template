import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel, Session

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

from app.core.config import settings # noqa
from app.models.user import User
from app.models.item import Item
from app.models.task import Task  # noqa

target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """Get database URL from settings with the same configuration as our tests"""
    return str(settings.SUPABASE_DATABASE_URL)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


def seed_data():
    from app.seeds.seeder import Seeder
    from sqlmodel import Session
    from app.core.db import engine

    with Session(engine) as session:
        seeder = Seeder(session)
        seeder.seed_all()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    from app.core.db import engine
    from app.core.config import settings
    
    # Configure SSL and other Supabase-specific settings
    connect_args = {
        "sslmode": "require",
        "application_name": "alembic",
        "client_encoding": "utf8",
        "options": "-c timezone=utc"
    }

    # Create a new engine with Supabase-specific settings
    configuration = {
        "sqlalchemy.url": str(settings.SUPABASE_DATABASE_URL),
        "sqlalchemy.connect_args": connect_args
    }

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        # Create a session using the same connection
        session = Session(bind=connection)
        
        try:
            with context.begin_transaction():
                context.run_migrations()
                # Seed data within the same transaction
                from app.seeds.seeder import Seeder
                seeder = Seeder(session)
                seeder.seed_all()
        finally:
            session.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
