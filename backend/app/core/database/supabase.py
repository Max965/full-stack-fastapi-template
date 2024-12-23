from sqlmodel import Session, create_engine
from pydantic import PostgresDsn
from typing import Dict, Any
from app.core.interfaces.database import IDatabase
from app.core.config import settings

class SupabaseDatabase(IDatabase):
    def __init__(self):
        self._engine = None

    def get_connection_url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql",
            username=settings.SUPABASE_DB_USER,
            password=settings.SUPABASE_DB_PASSWORD,
            host=settings.SUPABASE_DB_HOST,
            port=settings.SUPABASE_DB_PORT,
            path=f"/{settings.SUPABASE_DB_NAME}"
        )

    def get_connection_args(self) -> Dict[str, Any]:
        return {
            "dbname": settings.SUPABASE_DB_NAME,
            "user": settings.SUPABASE_DB_USER,
            "password": settings.SUPABASE_DB_PASSWORD,
            "host": settings.SUPABASE_DB_HOST,
            "port": settings.SUPABASE_DB_PORT,
            "sslmode": "require",
            "options": "-c client_encoding=UTF8",
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }

    def get_psycopg2_args(self) -> Dict[str, Any]:
        return self.get_connection_args()

    def get_engine(self):
        if not self._engine:
            url = str(self.get_connection_url())
            connect_args = self.get_connection_args()
            
            self._engine = create_engine(
                url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                connect_args=connect_args
            )
        return self._engine

    def get_session(self) -> Session:
        return Session(self.get_engine())