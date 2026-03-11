"""
Service layer for TodoList business logic.
Handles all CRUD operations for todo lists.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List
from app.models.todolist import TodoList
from app.models.collaborator import TodoListCollaborator, CollaboratorStatus
from app.schemas.todolist import TodoListCreate, TodoListUpdate
from fastapi import HTTPException, status


class TodoListService:

    @staticmethod
    def create_todolist(db: Session, todolist_data: TodoListCreate, user_id: int) -> TodoList:
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
    def _active_collab_join(query, user_id: int):
        """Helper: outerjoin collaborators table filtered to this user's active records."""
        return query.outerjoin(
            TodoListCollaborator,
            (TodoListCollaborator.todolist_id == TodoList.id) &
            (TodoListCollaborator.user_id == user_id) &
            (TodoListCollaborator.status == CollaboratorStatus.active)
        )

    @staticmethod
    def _access_filter(user_id: int):
        """Helper: OR condition for owner or active collaborator."""
        return or_(
            TodoList.user_id == user_id,
            TodoListCollaborator.user_id == user_id
        )

    @staticmethod
    def get_todolist_by_id(db: Session, todolist_id: int, user_id: int) -> TodoList:
        """Get a todolist by ID — accessible by owner or active collaborator."""
        query = TodoListService._active_collab_join(db.query(TodoList), user_id)
        db_todolist = query.filter(
            TodoList.id == todolist_id,
            TodoListService._access_filter(user_id)
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
        """Get all todolists the user owns or collaborates on."""
        query = TodoListService._active_collab_join(db.query(TodoList), user_id)
        return (
            query
            .filter(TodoListService._access_filter(user_id))
            .distinct()
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_todolists_count(db: Session, user_id: int) -> int:
        query = TodoListService._active_collab_join(db.query(TodoList), user_id)
        return (
            query
            .filter(TodoListService._access_filter(user_id))
            .distinct()
            .count()
        )

    @staticmethod
    def get_todolist_with_todos(db: Session, todolist_id: int, user_id: int) -> TodoList:
        """Get a todolist with all its todos eagerly loaded — owner or collaborator."""
        query = TodoListService._active_collab_join(
            db.query(TodoList).options(joinedload(TodoList.todos)),
            user_id
        )
        db_todolist = query.filter(
            TodoList.id == todolist_id,
            TodoListService._access_filter(user_id)
        ).first()
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
        """Update todolist metadata — owner only."""
        db_todolist = TodoListService.get_todolist_by_id(db, todolist_id, user_id)
        if db_todolist.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the list owner can update this list"
            )
        update_data = todolist_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_todolist, field, value)
        db.commit()
        db.refresh(db_todolist)
        return db_todolist

    @staticmethod
    def delete_todolist(db: Session, todolist_id: int, user_id: int) -> None:
        """Delete a todolist — owner only, cascades to all todos."""
        db_todolist = TodoListService.get_todolist_by_id(db, todolist_id, user_id)
        if db_todolist.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the list owner can delete this list"
            )
        db.delete(db_todolist)
        db.commit()
