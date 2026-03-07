"""
Service layer for Todo business logic.
Handles all CRUD operations and business rules.
Authorization is enforced by joining through TodoList to verify user ownership.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.todo import Todo, TodoStatus
from app.models.todolist import TodoList
from app.schemas.todo import TodoCreate, TodoUpdate
from fastapi import HTTPException, status


class TodoService:
    """
    Service class for Todo operations.
    Todos are owned by users indirectly via TodoList.
    All methods accept user_id and verify ownership through the TodoList.
    """

    @staticmethod
    def create_todo(db: Session, todo_data: TodoCreate, user_id: int) -> Todo:
        """
        Create a new todo in a todolist owned by the given user.

        Args:
            db: Database session
            todo_data: Todo creation data (must include todolist_id)
            user_id: ID of the authenticated user

        Returns:
            Todo: Created todo object

        Raises:
            HTTPException: 404 if the specified todolist doesn't exist or isn't owned by user
        """
        # Verify the todolist exists and belongs to this user
        todolist = db.query(TodoList).filter(
            TodoList.id == todo_data.todolist_id,
            TodoList.user_id == user_id
        ).first()
        if not todolist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"TodoList with id {todo_data.todolist_id} not found"
            )

        db_todo = Todo(
            title=todo_data.title,
            description=todo_data.description,
            due_date=todo_data.due_date,
            status=TodoStatus.PENDING,  # Always start with PENDING
            todolist_id=todo_data.todolist_id,
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo

    @staticmethod
    def get_todo_by_id(db: Session, todo_id: int, user_id: int) -> Todo:
        """
        Get a todo by its ID, verifying the user owns it via its TodoList.

        Args:
            db: Database session
            todo_id: ID of the todo to retrieve
            user_id: ID of the authenticated user

        Returns:
            Todo: Found todo object

        Raises:
            HTTPException: 404 if not found or user doesn't own it
        """
        db_todo = (
            db.query(Todo)
            .join(TodoList)
            .filter(Todo.id == todo_id, TodoList.user_id == user_id)
            .first()
        )
        if not db_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found"
            )
        return db_todo

    @staticmethod
    def get_all_todos(
        db: Session,
        user_id: int,
        todolist_id: Optional[int] = None,
        status_filter: Optional[TodoStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Todo]:
        """
        Get all todos for a user, optionally filtered by todolist and/or status.

        Args:
            db: Database session
            user_id: ID of the authenticated user
            todolist_id: Optional filter — only return todos from this list
            status_filter: Optional filter by status (Pending/Done/Cancelled)
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List[Todo]: List of todo objects
        """
        query = db.query(Todo).join(TodoList).filter(TodoList.user_id == user_id)

        if todolist_id is not None:
            query = query.filter(Todo.todolist_id == todolist_id)

        if status_filter is not None:
            query = query.filter(Todo.status == status_filter)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_todos_count(
        db: Session,
        user_id: int,
        todolist_id: Optional[int] = None,
        status_filter: Optional[TodoStatus] = None
    ) -> int:
        """
        Get the count of todos for a user with optional filters.

        Args:
            db: Database session
            user_id: ID of the authenticated user
            todolist_id: Optional filter by todolist
            status_filter: Optional filter by status

        Returns:
            int: Count of matching todos
        """
        query = db.query(Todo).join(TodoList).filter(TodoList.user_id == user_id)

        if todolist_id is not None:
            query = query.filter(Todo.todolist_id == todolist_id)

        if status_filter is not None:
            query = query.filter(Todo.status == status_filter)

        return query.count()

    @staticmethod
    def update_todo(
        db: Session,
        todo_id: int,
        todo_data: TodoUpdate,
        user_id: int
    ) -> Todo:
        """
        Update an existing todo (partial update supported).
        If todolist_id is being changed, verifies the user owns the target list.

        Args:
            db: Database session
            todo_id: ID of the todo to update
            todo_data: Update data (only provided fields will be updated)
            user_id: ID of the authenticated user

        Returns:
            Todo: Updated todo object

        Raises:
            HTTPException: 404 if todo not found, or target todolist not found/owned by user
        """
        db_todo = TodoService.get_todo_by_id(db, todo_id, user_id)

        update_data = todo_data.model_dump(exclude_unset=True)

        # If moving to a different todolist, verify the user owns that list too
        if 'todolist_id' in update_data:
            target_list = db.query(TodoList).filter(
                TodoList.id == update_data['todolist_id'],
                TodoList.user_id == user_id
            ).first()
            if not target_list:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"TodoList with id {update_data['todolist_id']} not found"
                )

        for field, value in update_data.items():
            setattr(db_todo, field, value)

        db.commit()
        db.refresh(db_todo)
        return db_todo

    @staticmethod
    def delete_todo(db: Session, todo_id: int, user_id: int) -> None:
        """
        Delete a todo by its ID.

        Args:
            db: Database session
            todo_id: ID of the todo to delete
            user_id: ID of the authenticated user

        Raises:
            HTTPException: 404 if todo not found or not owned by user
        """
        db_todo = TodoService.get_todo_by_id(db, todo_id, user_id)
        db.delete(db_todo)
        db.commit()
