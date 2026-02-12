"""
Todo SQLAlchemy model representing the todos table in the database.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
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
        user_id: Foreign key to the user who owns this todo (required)
        created_at: Timestamp when record was created (auto-generated)
        updated_at: Timestamp when record was last updated (auto-updated)
        owner: Relationship to the User who owns this todo
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
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

    # Relationship to user
    owner = relationship("User", back_populates="todos")

    def __repr__(self) -> str:
        """String representation of Todo object."""
        return f"<Todo(id={self.id}, title='{self.title}', status={self.status.value})>"
