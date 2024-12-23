from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from sqlmodel import Session
from pydantic import PostgresDsn

class IDatabase(ABC):
    @abstractmethod
    def get_connection_url(self) -> PostgresDsn:
        """Get database connection URL"""
        pass

    @abstractmethod
    def get_session(self) -> Session:
        """Get database session"""
        pass

    @abstractmethod
    def get_engine(self):
        """Get SQLAlchemy engine"""
        pass

    @abstractmethod
    def get_connection_args(self) -> Dict[str, Any]:
        """Get connection arguments"""
        pass

    @abstractmethod
    def get_psycopg2_args(self) -> Dict[str, Any]:
        """Get psycopg2-specific connection arguments"""
        pass 