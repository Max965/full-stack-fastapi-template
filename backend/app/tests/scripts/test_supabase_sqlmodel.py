from typing import Optional
from sqlmodel import Session, create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from pydantic import PostgresDsn

def get_database_url() -> PostgresDsn:
    """Construct and validate database URL using Pydantic"""
    return PostgresDsn.build(
        scheme="postgresql",
        username=settings.SUPABASE_DB_USER,
        password=settings.SUPABASE_DB_PASSWORD,
        host=settings.SUPABASE_DB_HOST,
        port=settings.SUPABASE_DB_PORT,
        path=f"/{settings.SUPABASE_DB_NAME}"
    )

def test_supabase_sqlmodel_connection() -> bool:
    """Test SQLModel connection to Supabase PostgreSQL"""
    try:
        # Create engine with validated URL
        engine = create_engine(str(get_database_url()), pool_pre_ping=True)

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
        raise
    except Exception as e:
        print("\n=== Unexpected Error ===")
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    test_supabase_sqlmodel_connection()