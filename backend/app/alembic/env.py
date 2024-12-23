from alembic import context
from sqlalchemy import engine_from_config, pool, text
from logging.config import fileConfig
import logging
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlmodel import SQLModel

# Import all models here
from app.models.user import User
from app.models.item import Item
from app.models.role import Role
from app.models.organisation import Organisation, Department, Employee

config = context.config
logger = logging.getLogger("alembic.env")

target_metadata = SQLModel.metadata

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    from app.core.db import db
    
    configuration = {
        "sqlalchemy.url": str(db.get_connection_url()),
        "sqlalchemy.connect_args": db.get_connection_args()
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
            compare_type=True,
            render_as_batch=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
