"""
Todo SQLAlchemy model representing the todos table in the database.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class TodoStatus(enum.Enum):
    """
    Enum for Todo status values.
    
    Attributes:
        PENDING: Task is pending (default)
        DONE: Task is completed
        CANCELLED: Task is cancelled
    """
    PENDING = "Pending"
    DONE = "Done"
    CANCELLED = "Cancelled"


class Todo(Base):
    """
    Todo model for storing task information.
    
    Attributes:
        id: Primary key, auto-incremented
        title: Todo title (max 60 characters, required)
        description: Detailed description (required)
        status: Current status (Pending/Done/Cancelled, defaults to Pending)
        due_date: Due date for the task (optional, stored as DateTime)
        created_at: Timestamp when record was created (auto-generated)
        updated_at: Timestamp when record was last updated (auto-updated)
    """
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(60), nullable=False, index=True)
    description = Column(Text, nullable=False)
    status = Column(
        SQLEnum(TodoStatus),
        nullable=False,
        default=TodoStatus.PENDING,
        index=True
    )
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        """String representation of Todo object."""
        return f"<Todo(id={self.id}, title='{self.title}', status={self.status.value})>"
