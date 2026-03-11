"""
Service layer for Todo business logic.
Authorization is enforced via TodoList — users can access todos in lists they
own or actively collaborate on. Only owners can delete todos.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.todo import Todo, TodoStatus
from app.models.todolist import TodoList
from app.models.collaborator import TodoListCollaborator, CollaboratorStatus
from app.schemas.todo import TodoCreate, TodoUpdate
from fastapi import HTTPException, status


def _access_query(db: Session, user_id: int):
    """
    Base query for todos the user can access (owner or active collaborator).
    Joins Todo → TodoList → TodoListCollaborator.
    """
    return (
        db.query(Todo)
        .join(TodoList)
        .outerjoin(
            TodoListCollaborator,
            (TodoListCollaborator.todolist_id == TodoList.id) &
            (TodoListCollaborator.user_id == user_id) &
            (TodoListCollaborator.status == CollaboratorStatus.active)
        )
        .filter(
            or_(
                TodoList.user_id == user_id,
                TodoListCollaborator.user_id == user_id
            )
        )
    )


def _can_access_list(db: Session, user_id: int, todolist_id: int) -> bool:
    """Returns True if user is owner or active collaborator of the given list."""
    result = (
        db.query(TodoList)
        .outerjoin(
            TodoListCollaborator,
            (TodoListCollaborator.todolist_id == TodoList.id) &
            (TodoListCollaborator.user_id == user_id) &
            (TodoListCollaborator.status == CollaboratorStatus.active)
        )
        .filter(
            TodoList.id == todolist_id,
            or_(
                TodoList.user_id == user_id,
                TodoListCollaborator.user_id == user_id
            )
        )
        .first()
    )
    return result is not None


class TodoService:

    @staticmethod
    def create_todo(db: Session, todo_data: TodoCreate, user_id: int) -> Todo:
        """Create a todo — user must be owner or active collaborator of the target list."""
        if not _can_access_list(db, user_id, todo_data.todolist_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"TodoList with id {todo_data.todolist_id} not found"
            )
        db_todo = Todo(
            title=todo_data.title,
            description=todo_data.description,
            due_date=todo_data.due_date,
            status=TodoStatus.PENDING,
            todolist_id=todo_data.todolist_id,
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo

    @staticmethod
    def get_todo_by_id(db: Session, todo_id: int, user_id: int) -> Todo:
        """Get a todo — accessible by owner or active collaborator."""
        db_todo = _access_query(db, user_id).filter(Todo.id == todo_id).first()
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
        """Get all todos the user can access, with optional filters."""
        query = _access_query(db, user_id)
        if todolist_id is not None:
            query = query.filter(Todo.todolist_id == todolist_id)
        if status_filter is not None:
            query = query.filter(Todo.status == status_filter)
        return query.distinct().offset(skip).limit(limit).all()

    @staticmethod
    def get_todos_count(
        db: Session,
        user_id: int,
        todolist_id: Optional[int] = None,
        status_filter: Optional[TodoStatus] = None
    ) -> int:
        query = _access_query(db, user_id)
        if todolist_id is not None:
            query = query.filter(Todo.todolist_id == todolist_id)
        if status_filter is not None:
            query = query.filter(Todo.status == status_filter)
        return query.distinct().count()

    @staticmethod
    def update_todo(
        db: Session,
        todo_id: int,
        todo_data: TodoUpdate,
        user_id: int
    ) -> Todo:
        """Update a todo — owner or collaborator. Moving to another list requires
        access to the target list as well."""
        db_todo = TodoService.get_todo_by_id(db, todo_id, user_id)
        update_data = todo_data.model_dump(exclude_unset=True)

        if 'todolist_id' in update_data:
            if not _can_access_list(db, user_id, update_data['todolist_id']):
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
        """Delete a todo — owner only. Collaborators receive 403."""
        db_todo = TodoService.get_todo_by_id(db, todo_id, user_id)

        # Verify user is the list owner, not just a collaborator
        todolist = db.query(TodoList).filter(TodoList.id == db_todo.todolist_id).first()
        if todolist.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the list owner can delete todos"
            )

        db.delete(db_todo)
        db.commit()
