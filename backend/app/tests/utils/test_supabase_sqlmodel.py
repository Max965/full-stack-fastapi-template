from typing import Optional
import psycopg2
from sqlmodel import Session, create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from pydantic import PostgresDsn
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def get_database_url() -> PostgresDsn:
    """Construct and validate database URL using Pydantic"""
    try:
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=settings.SUPABASE_DB_USER,
            password=settings.SUPABASE_DB_PASSWORD,
            host=settings.SUPABASE_DB_HOST,
            port=int(settings.SUPABASE_DB_PORT),
            path=f"/{settings.SUPABASE_DB_NAME}"
        )
    except Exception as e:
        logger.error(f"Failed to build database URL: {e}")
        raise

def get_safe_url(url: PostgresDsn) -> str:
    """Return URL with password masked"""
    parsed = urlparse(str(url))
    safe_netloc = f"{parsed.username}:****@{parsed.hostname}:{parsed.port}"
    return f"{parsed.scheme}://{safe_netloc}{parsed.path}"

def test_supabase_sqlmodel_connection() -> bool:
    """Test SQLModel connection to Supabase PostgreSQL"""
    try:
        db_url = get_database_url()
        logger.info(f"Attempting to connect to database at: {get_safe_url(db_url)}")
        
        # Modified engine creation with proper encoding settings
        engine = create_engine(
            str(db_url), 
            pool_pre_ping=True,
            connect_args={
                "sslmode": "require",
                "client_encoding": "utf8",
                "options": "-c client_encoding=utf8",
                "application_name": "supabase_test"
            }
        )
        
        # Test connection with a simple query
        with Session(engine) as session:
            result: Optional[int] = session.exec(select(1)).first()
            assert result == 1, "Database query did not return expected result"
            
        print("\n=== Supabase PostgreSQL Connection Test ===")
        print("Connection successful!")
        print(f"Test query result: {result}")
        
        return True
        
    except SQLAlchemyError as e:
        print("\n=== Supabase PostgreSQL Connection Error ===")
        print(f"Database Error: {str(e)}")
        logger.error(f"Database connection failed: {e}", exc_info=True)
        raise
    except Exception as e:
        print("\n=== Unexpected Error ===")
        print(f"Error: {str(e)}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise

def test_raw_connection():
    try:
        conn = psycopg2.connect(
            dbname=settings.SUPABASE_DB_NAME,
            user=settings.SUPABASE_DB_USER,
            password=settings.SUPABASE_DB_PASSWORD,
            host=settings.SUPABASE_DB_HOST,
            port=settings.SUPABASE_DB_PORT,
            sslmode='require',
            options="-c client_encoding=UTF8",
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5
        )
        print("Connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        logger.error(f"Raw connection failed: {e}", exc_info=True)
        raise

def test_sqlalchemy_connection() -> bool:
    """Test SQLAlchemy connection using the same URL configuration as migrations"""
    try:
        from app.core.config import settings
        from sqlalchemy import create_engine, text
        
        # Get the URL exactly as used in migrations
        db_url = str(settings.SUPABASE_DATABASE_URL)
        logger.info(f"Attempting to connect to database at: {get_safe_url(db_url)}")
        
        # Create engine with the same configuration as used in migrations
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            connect_args={
                "sslmode": "require",
                "application_name": "migration_test",
                "client_encoding": "utf8",
                "options": "-c timezone=utc"
            }
        )
        
        # Test connection with a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            assert result == 1, "Database query did not return expected result"
            
        print("\n=== Migration Database Connection Test ===")
        print("Connection successful!")
        print(f"Test query result: {result}")
        
        return True
        
    except Exception as e:
        print("\n=== Migration Database Connection Error ===")
        print(f"Error: {str(e)}")
        logger.error(f"Migration connection failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
   # test_raw_connection()
    test_sqlalchemy_connection()