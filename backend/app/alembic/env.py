from alembic import context
from sqlalchemy import engine_from_config, pool, text
import logging
from sqlmodel import SQLModel
import os

# Import all models in the correct order
from app.models.role import Role  # No foreign keys
from app.models.user import User  # References Role
from app.models.task import Task
from app.models.auth import Token, TokenPayload, NewPassword

config = context.config

target_metadata = SQLModel.metadata
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alembic.env")

RESET_MIGRATION_HISTORY = os.getenv("RESET_MIGRATION_HISTORY", "false").lower() == "true"
DROP_ALL_TABLES = os.getenv("DROP_ALL_TABLES", "false").lower() == "true"

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    logger.info("Running migrations in online mode")
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
        if DROP_ALL_TABLES:
            logger.info("Running in drop all tables mode")
            drop_all_tables(connection)
        logger.info(f"RESET_MIGRATION_HISTORY: {RESET_MIGRATION_HISTORY}")
        if RESET_MIGRATION_HISTORY:
            logger.info("Running in reset migration history mode")
            reset_migration_history(connection)
        
        run_migrations(connection)

def log_existing_tables(connection):
    existing_tables = connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")).fetchall()
    logger.info("Existing tables in the database:")
    if existing_tables:
        for table in existing_tables:
            logger.info(f"- {table[0]}")
    else:
        logger.info("No tables found in the database")

def drop_all_tables(connection):
    log_existing_tables(connection)
    logger.info("Dropping all tables in the database")
    try:
        connection.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public; CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num));"))
        connection.commit()  # Ensure the transaction is committed
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
    log_existing_tables(connection)
def reset_migration_history(connection):
    logger.info("Resetting migration history")
    connection.execute(text("DELETE FROM alembic_version"))
    connection.commit()

def run_migrations(connection):
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
