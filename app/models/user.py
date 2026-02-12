"""
User SQLAlchemy model representing the users table in the database.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    User model for storing user account information.
    
    Attributes:
        id: Primary key, auto-incremented
        email: User's email address (unique, indexed, required)
        username: User's username (unique, required)
        hashed_password: Bcrypt hashed password (required)
        is_active: Whether the user account is active (defaults to True)
        created_at: Timestamp when the user was created (auto-generated)
        updated_at: Timestamp when the user was last updated (auto-updated)
        todos: Relationship to Todo items owned by this user
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
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

    # Relationship to todos
    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")
