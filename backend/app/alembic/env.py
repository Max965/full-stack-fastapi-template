import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel, Session
import logging
from sqlalchemy import inspect
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic import command
from sqlalchemy import text

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
logger = logging.getLogger("alembic.env")

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
from app.models.role import Role  # Make sure this is imported

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


def include_object(object, name, type_, reflected, compare_to):
    """
    Helper to determine if an object should be included in the migration.
    Returns False for objects that don't exist in the database yet during --autogenerate
    """
    try:
        # If we can't reflect the object, it's new
        if not reflected:
            return True
        return True
    except Exception as e:
        logger.info(f"Skipping comparison for {name} due to: {e}")
        return True


def get_current_head():
    """Get the current head revision or None if no revisions exist"""
    script = context.script.get_revision("head")
    return script.revision if script else None


def reset_db_revision(connection):
    """Reset the database revision directly using SQL"""
    try:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
        connection.execute(text("""
            CREATE TABLE alembic_version (
                version_num VARCHAR(32) NOT NULL,
                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
            )
        """))
        # Don't insert base revision - let alembic handle it
        logger.info("Successfully reset alembic_version table")
    except Exception as e:
        logger.error(f"Error resetting database revision: {e}")
        raise


def check_current_head(connection):
    """Check if the current head exists in our versions"""
    migration_ctx = MigrationContext.configure(connection)
    current_heads = migration_ctx.get_current_heads()
    
    if len(current_heads) > 1:
        logger.warning("Multiple heads detected, resetting to base")
        reset_db_revision(connection)
        # After reset, stamp with the current head
        script = ScriptDirectory.from_config(config)
        head_revision = script.get_current_head()
        if head_revision:
            connection.execute(
                text(f"INSERT INTO alembic_version (version_num) VALUES ('{head_revision}')")
            )
            logger.info(f"Stamped database with current head: {head_revision}")
    
    return migration_ctx.get_current_heads()


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
            check_current_head(connection)
            context.run_migrations()
        
        # Run seeding after migrations complete
        with Session(connectable) as session:
            from app.seeds.seeder import Seeder
            seeder = Seeder(session)
            seeder.seed_all()


def process_revision_directives(context, revision, directives):
    """Allow creating initial migration even if no revisions exist"""
    if not directives[0].head_revision and not get_current_head():
        directives[0].head_revision = None


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
