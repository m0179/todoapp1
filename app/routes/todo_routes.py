"""
API routes for Todo CRUD operations.
Defines all REST endpoints for managing todos.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse, TodoListResponse
from app.services.todo_service import TodoService
from app.models.todo import TodoStatus
from app.dependencies.auth import get_current_user
from app.models.user import User

# Create router with prefix and tags for organization
router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)


@router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new todo",
    description="Create a new todo item with title, description, and optional due date. Status defaults to Pending."
)
def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TodoResponse:
    """
    Create a new todo.
    
    - **title**: Required, max 60 characters
    - **description**: Required
    - **due_date**: Optional, must be in the future
    - **status**: Automatically set to Pending
    """
    return TodoService.create_todo(db, todo, current_user.id)


@router.get(
    "/",
    response_model=TodoListResponse,
    summary="Get all todos",
    description="Retrieve all todos with optional filtering by status and pagination support."
)
def get_todos(
    status_filter: Optional[TodoStatus] = Query(
        None,
        description="Filter todos by status (Pending, Done, or Cancelled)"
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip for pagination"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of records to return (max 1000)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TodoListResponse:
    """
    Get all todos with optional filtering.
    
    - **status_filter**: Optional filter by status (Pending/Done/Cancelled)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100, max: 1000)
    """
    todos = TodoService.get_all_todos(db, current_user.id, status_filter, skip, limit)
    total = TodoService.get_todos_count(db, current_user.id, status_filter)
    return TodoListResponse(todos=todos, total=total)


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Get a todo by ID",
    description="Retrieve a specific todo by its ID."
)
def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TodoResponse:
    """
    Get a single todo by ID.
    
    - **todo_id**: ID of the todo to retrieve
    
    Returns 404 if todo not found.
    """
    return TodoService.get_todo_by_id(db, todo_id, current_user.id)


@router.put(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Update a todo",
    description="Update an existing todo. All fields are optional (partial update supported)."
)
def update_todo(
    todo_id: int,
    todo: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TodoResponse:
    """
    Update an existing todo (partial update supported).
    
    - **todo_id**: ID of the todo to update
    - **title**: Optional, max 60 characters
    - **description**: Optional
    - **status**: Optional (Pending/Done/Cancelled)
    - **due_date**: Optional, must be in the future
    
    Only provided fields will be updated. Returns 404 if todo not found.
    """
    return TodoService.update_todo(db, todo_id, todo, current_user.id)


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a todo",
    description="Delete a todo by its ID."
)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a todo by ID.
    
    - **todo_id**: ID of the todo to delete
    
    Returns 204 No Content on success, 404 if todo not found.
    """
    TodoService.delete_todo(db, todo_id, current_user.id)
