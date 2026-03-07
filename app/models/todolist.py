"""
TodoList SQLAlchemy model representing the todolists table in the database.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class TodoList(Base):
    """
    TodoList model for organizing todos into named lists.

    Attributes:
        id: Primary key, auto-incremented
        name: List name (max 100 characters, required)
        description: Optional description of the list
        color: Optional hex color code for UI (e.g., #FF5733)
        icon: Optional icon or emoji identifier
        user_id: Foreign key to the user who owns this list
        created_at: Timestamp when record was created (auto-generated)
        updated_at: Timestamp when record was last updated (auto-updated)
        owner: Relationship to the User who owns this list
        todos: Relationship to todos belonging to this list
    """
    __tablename__ = "todolists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)
    icon = Column(String(50), nullable=True)
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

    # Relationships
    owner = relationship("User", back_populates="todolists")
    todos = relationship("Todo", back_populates="todolist", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of TodoList object."""
        return f"<TodoList(id={self.id}, name='{self.name}', user_id={self.user_id})>"
