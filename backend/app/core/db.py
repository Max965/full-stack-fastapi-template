from sqlmodel import SQLModel, Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models.user import User, UserCreate
from app.core.database.supabase import SupabaseDatabase

db = SupabaseDatabase()
engine = db.get_engine()

#SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    return db.get_session()

def init_db(session: Session) -> None:
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
