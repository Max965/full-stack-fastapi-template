from sqlmodel import SQLModel, Field
import uuid

class Role(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=50, unique=True, index=True)
    description: str | None = Field(default=None, max_length=255) 