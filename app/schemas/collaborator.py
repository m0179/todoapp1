from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.collaborator import CollaboratorStatus


class InviteRequest(BaseModel):
    email_or_username: str = Field(..., description="Email or username of the user to invite")


class CollaboratorResponse(BaseModel):
    id: int
    todolist_id: int
    user_id: Optional[int] = None
    invited_email: Optional[str] = None
    status: CollaboratorStatus
    invited_at: datetime

    class Config:
        from_attributes = True
