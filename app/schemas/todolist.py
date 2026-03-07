"""
Pydantic schemas for TodoList API request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
import re

from app.schemas.todo import TodoResponse


class TodoListBase(BaseModel):
    """Base schema with common TodoList fields."""
    name: str = Field(..., min_length=1, max_length=100, description="List name (required)")
    description: Optional[str] = Field(None, description="Optional description of the list")
    color: Optional[str] = Field(None, description="Hex color code (e.g., #FF5733)")
    icon: Optional[str] = Field(None, max_length=50, description="Icon or emoji identifier")

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate that color is a valid 6-digit hex code."""
        if v is not None and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex code (e.g., #FF5733)')
        return v


class TodoListCreate(TodoListBase):
    """Schema for creating a new TodoList."""
    pass


class TodoListUpdate(BaseModel):
    """
    Schema for updating an existing TodoList.
    All fields are optional to support partial updates.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="List name")
    description: Optional[str] = Field(None, description="Description of the list")
    color: Optional[str] = Field(None, description="Hex color code (e.g., #FF5733)")
    icon: Optional[str] = Field(None, max_length=50, description="Icon or emoji identifier")

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate that color is a valid 6-digit hex code."""
        if v is not None and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex code (e.g., #FF5733)')
        return v


class TodoListResponse(TodoListBase):
    """Schema for TodoList responses (single todolist)."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TodoListWithTodos(TodoListResponse):
    """Schema for TodoList response including its nested todos."""
    todos: List[TodoResponse] = []
