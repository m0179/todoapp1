"""
API routes for TodoList CRUD operations.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.todolist import TodoListCreate, TodoListUpdate, TodoListResponse, TodoListWithTodos
from app.services.todolist_service import TodoListService
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/todolists",
    tags=["todolists"]
)


@router.post(
    "/",
    response_model=TodoListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new todo list",
    description="Create a new named list to organize your todos."
)
def create_todolist(
    todolist: TodoListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TodoListResponse:
    """
    Create a new todo list.

    - **name**: Required, max 100 characters
    - **description**: Optional description
    - **color**: Optional hex color code (e.g., #FF5733)
    - **icon**: Optional icon or emoji
    """
    return TodoListService.create_todolist(db, todolist, current_user.id)


@router.get(
    "/",
    response_model=List[TodoListResponse],
    summary="Get all todo lists",
    description="Retrieve all todo lists belonging to the current user."
)
def get_todolists(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[TodoListResponse]:
    """
    Get all todo lists for the current user.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100, max: 1000)
    """
    return TodoListService.get_all_todolists(db, current_user.id, skip, limit)


@router.get(
    "/{todolist_id}",
    response_model=TodoListResponse,
    summary="Get a todo list by ID",
    description="Retrieve a specific todo list by its ID."
)
def get_todolist(
    todolist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TodoListResponse:
    """
    Get a single todo list by ID. Returns 404 if not found.
    """
    return TodoListService.get_todolist_by_id(db, todolist_id, current_user.id)


@router.get(
    "/{todolist_id}/todos",
    response_model=TodoListWithTodos,
    summary="Get a todo list with its todos",
    description="Retrieve a todo list along with all todos nested inside it."
)
def get_todolist_with_todos(
    todolist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TodoListWithTodos:
    """
    Get a todo list and all its todos in a single response.
    """
    return TodoListService.get_todolist_with_todos(db, todolist_id, current_user.id)


@router.put(
    "/{todolist_id}",
    response_model=TodoListResponse,
    summary="Update a todo list",
    description="Update an existing todo list. All fields are optional (partial update supported)."
)
def update_todolist(
    todolist_id: int,
    todolist: TodoListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TodoListResponse:
    """
    Update an existing todo list (partial update supported).

    - **name**: Optional, max 100 characters
    - **description**: Optional
    - **color**: Optional hex color code
    - **icon**: Optional icon or emoji

    Returns 404 if todo list not found.
    """
    return TodoListService.update_todolist(db, todolist_id, todolist, current_user.id)


@router.delete(
    "/{todolist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a todo list",
    description="Delete a todo list by ID. All todos inside it will also be deleted."
)
def delete_todolist(
    todolist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a todo list and all its todos. Returns 404 if not found.
    """
    TodoListService.delete_todolist(db, todolist_id, current_user.id)
