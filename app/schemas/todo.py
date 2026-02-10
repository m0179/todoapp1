"""
Pydantic schemas for Todo API request/response validation.
These schemas define the structure and validation rules for API data.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from app.models.todo import TodoStatus


class TodoBase(BaseModel):
    """
    Base schema with common Todo fields.
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=60,
        description="Todo title (required, max 60 characters)"
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Todo description (required)"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Due date for the todo (optional, must be in future)"
    )

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """
        Validate that due_date is in the future.
        
        Args:
            v: The due_date value
            
        Returns:
            The validated due_date
            
        Raises:
            ValueError: If due_date is in the past
        """
        if v is not None and v < datetime.now(v.tzinfo):
            raise ValueError('due_date must be in the future')
        return v


class TodoCreate(TodoBase):
    """
    Schema for creating a new Todo.
    Status defaults to PENDING and is not required in request.
    """
    pass


class TodoUpdate(BaseModel):
    """
    Schema for updating an existing Todo.
    All fields are optional to support partial updates.
    """
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=60,
        description="Todo title (optional)"
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        description="Todo description (optional)"
    )
    status: Optional[TodoStatus] = Field(
        None,
        description="Todo status (optional)"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Due date for the todo (optional)"
    )

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate that due_date is in the future."""
        if v is not None and v < datetime.now(v.tzinfo):
            raise ValueError('due_date must be in the future')
        return v


class TodoResponse(TodoBase):
    """
    Schema for Todo responses (single todo).
    Includes all fields from the database model.
    """
    id: int
    status: TodoStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Allows creation from SQLAlchemy models


class TodoListResponse(BaseModel):
    """
    Schema for list of todos response.
    """
    todos: List[TodoResponse]
    total: int = Field(..., description="Total number of todos")

    class Config:
        """Pydantic configuration."""
        from_attributes = True
