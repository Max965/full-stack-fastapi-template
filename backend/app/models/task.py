from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import text as sa_text
from .user import User

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"
    REOPENED = "reopened"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(SQLModel, table=True):
    """Task model with all fields"""
    __tablename__ = "tasks"
    
    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True), 
            primary_key=True, 
            server_default=sa_text('gen_random_uuid()')
        )
    )
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    
    # Use existing enum types without creating new ones
    status: TaskStatus = Field(
        sa_column=Column(
            "status",
            SQLEnum(TaskStatus, name="taskstatus", create_type=False),
            nullable=False,
            default=TaskStatus.TODO
        )
    )
    priority: TaskPriority = Field(
        sa_column=Column(
            "priority",
            SQLEnum(TaskPriority, name="taskpriority", create_type=False),
            nullable=False,
            default=TaskPriority.MEDIUM
        )
    )
    
    # Dates
    due_date: datetime | None = Field(default=None)
    start_date: datetime | None = Field(default=None)
    completed_date: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    owner_id: UUID = Field(foreign_key="user.id", nullable=False)
    creator_id: UUID = Field(foreign_key="user.id", nullable=False)
    parent_id: UUID | None = Field(foreign_key="tasks.id", nullable=True, default=None)
    
    owner: User = Relationship(
        back_populates="owned_tasks",
        sa_relationship_kwargs={"foreign_keys": "[Task.owner_id]"}
    )
    creator: User = Relationship(
        back_populates="created_tasks",
        sa_relationship_kwargs={"foreign_keys": "[Task.creator_id]"}
    )
    subtasks: List["Task"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"foreign_keys": "[Task.parent_id]"}
    )
    parent: Optional["Task"] = Relationship(
        back_populates="subtasks"
    )