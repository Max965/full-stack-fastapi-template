from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4

class Organisation(SQLModel, table=True):
    __tablename__ = "organisations"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    domain: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    departments: List["Department"] = Relationship(back_populates="organisation")
    employees: List["Employee"] = Relationship(back_populates="organisation")

class Department(SQLModel, table=True):
    __tablename__ = "departments"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    organisation_id: UUID = Field(foreign_key="organisations.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    organisation: Organisation = Relationship(back_populates="departments")
    employees: List["Employee"] = Relationship(back_populates="department")

class Employee(SQLModel, table=True):
    __tablename__ = "employees"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    organisation_id: UUID = Field(foreign_key="organisations.id")
    department_id: Optional[UUID] = Field(foreign_key="departments.id", nullable=True)
    position: str
    level: int
    reports_to_id: Optional[UUID] = Field(foreign_key="employees.id", nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship()
    organisation: Organisation = Relationship(back_populates="employees")
    department: Optional[Department] = Relationship(back_populates="employees")
    reports_to: Optional["Employee"] = Relationship(
        sa_relationship_kwargs={
            "remote_side": "Employee.id",
            "primaryjoin": "Employee.reports_to_id==Employee.id"
        }
    )
    subordinates: List["Employee"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Employee.reports_to_id==Employee.id",
            "back_populates": "reports_to"
        }
    )

    class Config:
        arbitrary_types_allowed = True