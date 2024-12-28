from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Column
from uuid import UUID
from sqlalchemy import text as sa_text

class Role(SQLModel, table=True):
    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            server_default=sa_text('gen_random_uuid()'),
            primary_key=True
        )
    )
    name: str = Field(max_length=50, unique=True, index=True)
    description: str | None = Field(default=None, max_length=255)