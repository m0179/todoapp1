"""
Service layer for TodoList business logic.
Handles all CRUD operations for todo lists.
"""
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.models.todolist import TodoList
from app.schemas.todolist import TodoListCreate, TodoListUpdate
from fastapi import HTTPException, status


class TodoListService:
    """
    Service class for TodoList operations.
    All methods take user_id to enforce ownership-based authorization.
    """

    @staticmethod
    def create_todolist(db: Session, todolist_data: TodoListCreate, user_id: int) -> TodoList:
        """
        Create a new todo list for the given user.

        Args:
            db: Database session
            todolist_data: TodoList creation data
            user_id: ID of the user creating the list

        Returns:
            TodoList: Created todolist object
        """
        db_todolist = TodoList(
            name=todolist_data.name,
            description=todolist_data.description,
            color=todolist_data.color,
            icon=todolist_data.icon,
            user_id=user_id,
        )
        db.add(db_todolist)
        db.commit()
        db.refresh(db_todolist)
        return db_todolist

    @staticmethod
    def get_todolist_by_id(db: Session, todolist_id: int, user_id: int) -> TodoList:
        """
        Get a todolist by its ID, verifying it belongs to the given user.

        Args:
            db: Database session
            todolist_id: ID of the todolist to retrieve
            user_id: ID of the user who must own the list

        Returns:
            TodoList: Found todolist object

        Raises:
            HTTPException: 404 if not found or not owned by user
        """
        db_todolist = db.query(TodoList).filter(
            TodoList.id == todolist_id,
            TodoList.user_id == user_id
        ).first()
        if not db_todolist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"TodoList with id {todolist_id} not found"
            )
        return db_todolist

    @staticmethod
    def get_all_todolists(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[TodoList]:
        """
        Get all todolists for a specific user with pagination.

        Args:
            db: Database session
            user_id: ID of the user who owns the lists
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List[TodoList]: List of todolist objects
        """
        return (
            db.query(TodoList)
            .filter(TodoList.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_todolists_count(db: Session, user_id: int) -> int:
        """
        Get the total number of todolists for a user.

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            int: Count of todolists
        """
        return db.query(TodoList).filter(TodoList.user_id == user_id).count()

    @staticmethod
    def get_todolist_with_todos(db: Session, todolist_id: int, user_id: int) -> TodoList:
        """
        Get a todolist with all its todos eagerly loaded.

        Args:
            db: Database session
            todolist_id: ID of the todolist to retrieve
            user_id: ID of the user who must own the list

        Returns:
            TodoList: Todolist with .todos already populated

        Raises:
            HTTPException: 404 if not found or not owned by user
        """
        db_todolist = (
            db.query(TodoList)
            .options(joinedload(TodoList.todos))
            .filter(TodoList.id == todolist_id, TodoList.user_id == user_id)
            .first()
        )
        if not db_todolist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"TodoList with id {todolist_id} not found"
            )
        return db_todolist

    @staticmethod
    def update_todolist(
        db: Session,
        todolist_id: int,
        todolist_data: TodoListUpdate,
        user_id: int
    ) -> TodoList:
        """
        Update an existing todolist (partial update supported).

        Args:
            db: Database session
            todolist_id: ID of the todolist to update
            todolist_data: Update data (only provided fields will be updated)
            user_id: ID of the user who owns the list

        Returns:
            TodoList: Updated todolist object

        Raises:
            HTTPException: 404 if not found or not owned by user
        """
        db_todolist = TodoListService.get_todolist_by_id(db, todolist_id, user_id)

        update_data = todolist_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_todolist, field, value)

        db.commit()
        db.refresh(db_todolist)
        return db_todolist

    @staticmethod
    def delete_todolist(db: Session, todolist_id: int, user_id: int) -> None:
        """
        Delete a todolist by its ID (cascades to all its todos).

        Args:
            db: Database session
            todolist_id: ID of the todolist to delete
            user_id: ID of the user who owns the list

        Raises:
            HTTPException: 404 if not found or not owned by user
        """
        db_todolist = TodoListService.get_todolist_by_id(db, todolist_id, user_id)
        db.delete(db_todolist)
        db.commit()
