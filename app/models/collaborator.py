"""
TodoListCollaborator SQLAlchemy model representing the todolist_collaborators table.
"""
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CollaboratorStatus(str, enum.Enum):
    pending = "pending"
    active = "active"


class TodoListCollaborator(Base):
    __tablename__ = "todolist_collaborators"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    todolist_id = Column(Integer, ForeignKey("todolists.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    invited_email = Column(String(255), nullable=True, index=True)
    status = Column(Enum(CollaboratorStatus), nullable=False, default=CollaboratorStatus.pending)
    invited_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    todolist = relationship("TodoList", back_populates="collaborators")
    user = relationship("User", back_populates="collaborations")
