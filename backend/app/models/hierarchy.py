from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4

class HierarchyRelationship(SQLModel, table=True):
    __tablename__ = "hierarchy_relationships"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    manager_id: UUID = Field(foreign_key="user.id")
    worker_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    manager: "User" = Relationship(
        back_populates="managed_workers",
        sa_relationship_kwargs={"foreign_keys": [manager_id]}
    )
    worker: "User" = Relationship(
        back_populates="reports_to",
        sa_relationship_kwargs={"foreign_keys": [worker_id]}
    )

    class Config:
        arbitrary_types_allowed = True 