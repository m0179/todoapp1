"""
Service layer for Todo business logic.
Handles all CRUD operations and business rules.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.todo import Todo, TodoStatus
from app.schemas.todo import TodoCreate, TodoUpdate
from fastapi import HTTPException, status


class TodoService:
    """
    Service class for Todo operations.
    Encapsulates business logic and database operations.
    """

    @staticmethod
    def create_todo(db: Session, todo_data: TodoCreate, user_id: int) -> Todo:
        """
        Create a new todo item.
        
        Args:
            db: Database session
            todo_data: Todo creation data
            user_id: ID of the user creating the todo
            
        Returns:
            Todo: Created todo object
            
        Example:
            todo = TodoService.create_todo(db, TodoCreate(
                title="Buy groceries",
                description="Milk, eggs, bread"
            ), user_id=1)
        """
        db_todo = Todo(
            title=todo_data.title,
            description=todo_data.description,
            due_date=todo_data.due_date,
            status=TodoStatus.PENDING,  # Always start with PENDING
            user_id=user_id
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo

    @staticmethod
    def get_todo_by_id(db: Session, todo_id: int, user_id: int) -> Todo:
        """
        Get a todo by its ID for a specific user.
        
        Args:
            db: Database session
            todo_id: ID of the todo to retrieve
            user_id: ID of the user who owns the todo
            
        Returns:
            Todo: Found todo object
            
        Raises:
            HTTPException: If todo not found or doesn't belong to user (404)
        """
        db_todo = db.query(Todo).filter(
            Todo.id == todo_id,
            Todo.user_id == user_id
        ).first()
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
        status_filter: Optional[TodoStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Todo]:
        """
        Get all todos for a specific user with optional filtering.
        
        Args:
            db: Database session
            user_id: ID of the user who owns the todos
            status_filter: Optional status filter (Pending/Done/Cancelled)
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List[Todo]: List of todo objects
            
        Example:
            # Get all pending todos for user
            todos = TodoService.get_all_todos(db, user_id=1, status_filter=TodoStatus.PENDING)
            
            # Get all todos with pagination
            todos = TodoService.get_all_todos(db, user_id=1, skip=10, limit=20)
        """
        query = db.query(Todo).filter(Todo.user_id == user_id)
        
        # Apply status filter if provided
        if status_filter:
            query = query.filter(Todo.status == status_filter)
        
        # Apply pagination
        todos = query.offset(skip).limit(limit).all()
        return todos

    @staticmethod
    def get_todos_count(
        db: Session,
        user_id: int,
        status_filter: Optional[TodoStatus] = None
    ) -> int:
        """
        Get count of todos for a specific user with optional filtering.
        
        Args:
            db: Database session
            user_id: ID of the user who owns the todos
            status_filter: Optional status filter
            
        Returns:
            int: Count of todos
        """
        query = db.query(Todo).filter(Todo.user_id == user_id)
        if status_filter:
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
        
        Args:
            db: Database session
            todo_id: ID of the todo to update
            todo_data: Update data (only provided fields will be updated)
            user_id: ID of the user who owns the todo
            
        Returns:
            Todo: Updated todo object
            
        Raises:
            HTTPException: If todo not found or doesn't belong to user (404)
            
        Example:
            # Update only status
            todo = TodoService.update_todo(
                db,
                todo_id=1,
                TodoUpdate(status=TodoStatus.DONE),
                user_id=1
            )
        """
        db_todo = TodoService.get_todo_by_id(db, todo_id, user_id)
        
        # Update only the fields that were provided (exclude_unset=True)
        update_data = todo_data.model_dump(exclude_unset=True)
        
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
            user_id: ID of the user who owns the todo
            
        Raises:
            HTTPException: If todo not found or doesn't belong to user (404)
            
        Example:
            TodoService.delete_todo(db, todo_id=1, user_id=1)
        """
        db_todo = TodoService.get_todo_by_id(db, todo_id, user_id)
        db.delete(db_todo)
        db.commit()
