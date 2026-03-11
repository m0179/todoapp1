"""
Service layer for TodoList collaboration.
Handles invites, role checks, and pending invite activation on registration.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.todolist import TodoList
from app.models.collaborator import TodoListCollaborator, CollaboratorStatus
from app.models.user import User


class CollaboratorService:

    @staticmethod
    def invite_user(
        db: Session,
        todolist_id: int,
        owner_id: int,
        email_or_username: str
    ) -> TodoListCollaborator:
        """
        Invite a user to collaborate on a todolist.
        - If the user exists: grants immediate active access.
        - If the user doesn't exist and input is an email: creates a pending invite
          and logs a mock email to console.
        - If input is a username and user not found: raises 404.
        """
        # Check list exists
        todolist = db.query(TodoList).filter(TodoList.id == todolist_id).first()
        if not todolist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"TodoList with id {todolist_id} not found"
            )
        # Only the owner can invite
        if todolist.user_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the list owner can invite collaborators"
            )

        # Try to find existing user by email or username
        user = db.query(User).filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()

        if user:
            if user.id == owner_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You are already the owner of this list"
                )
            existing = db.query(TodoListCollaborator).filter(
                TodoListCollaborator.todolist_id == todolist_id,
                TodoListCollaborator.user_id == user.id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already a collaborator on this list"
                )
            collab = TodoListCollaborator(
                todolist_id=todolist_id,
                user_id=user.id,
                status=CollaboratorStatus.active
            )
        else:
            # User not found — only allow pending invite if input looks like an email
            if "@" not in email_or_username:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User '{email_or_username}' not found"
                )
            existing = db.query(TodoListCollaborator).filter(
                TodoListCollaborator.todolist_id == todolist_id,
                TodoListCollaborator.invited_email == email_or_username
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An invite has already been sent to this email"
                )
            collab = TodoListCollaborator(
                todolist_id=todolist_id,
                invited_email=email_or_username,
                status=CollaboratorStatus.pending
            )
            # Mock email — log to console (replace with real email service later)
            print(
                f"\n[MOCK EMAIL] ─────────────────────────────────────────\n"
                f"  To: {email_or_username}\n"
                f"  Subject: You've been invited to collaborate on '{todolist.name}'\n"
                f"  Body: Sign up at http://localhost:8000/auth/register\n"
                f"         Once registered, you'll automatically get access.\n"
                f"──────────────────────────────────────────────────────\n"
            )

        db.add(collab)
        db.commit()
        db.refresh(collab)
        return collab

    @staticmethod
    def activate_pending_invites(db: Session, user: User) -> None:
        """
        Called after a new user registers. Finds all pending invites for their
        email and activates them by linking to the new user account.
        """
        pending = db.query(TodoListCollaborator).filter(
            TodoListCollaborator.invited_email == user.email,
            TodoListCollaborator.status == CollaboratorStatus.pending
        ).all()
        for invite in pending:
            invite.user_id = user.id
            invite.status = CollaboratorStatus.active
        if pending:
            db.commit()
