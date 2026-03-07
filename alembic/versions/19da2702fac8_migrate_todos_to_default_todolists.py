"""migrate todos to default todolists

Revision ID: 19da2702fac8
Revises: 51a5b079280f
Create Date: 2026-03-06 00:55:40.264612

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, select


# revision identifiers, used by Alembic.
revision: str = '19da2702fac8'
down_revision: Union[str, Sequence[str], None] = '51a5b079280f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Data migration: create a default 'My Tasks' todolist for each user
    and assign all their existing todos to it.
    """
    # Define lightweight table references for raw SQL operations
    users_table = table('users', column('id', sa.Integer))
    todos_table = table(
        'todos',
        column('id', sa.Integer),
        column('user_id', sa.Integer),
        column('todolist_id', sa.Integer),
    )

    connection = op.get_bind()
    users = connection.execute(select(users_table.c.id)).fetchall()

    for user in users:
        user_id = user[0]

        # Create default "My Tasks" todolist for this user.
        # Use RETURNING id (PostgreSQL) to get the new row's ID reliably.
        result = connection.execute(
            sa.text(
                "INSERT INTO todolists (name, description, user_id, created_at, updated_at) "
                "VALUES (:name, :description, :user_id, now(), now()) "
                "RETURNING id"
            ),
            {"name": "My Tasks", "description": "Default todo list", "user_id": user_id}
        )
        todolist_id = result.scalar()

        # Assign all existing todos belonging to this user to the new list
        connection.execute(
            todos_table.update()
            .where(todos_table.c.user_id == user_id)
            .values(todolist_id=todolist_id)
        )


def downgrade() -> None:
    """Undo data migration: clear todolist_id from todos and delete default lists."""
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE todos SET todolist_id = NULL"))
    connection.execute(sa.text("DELETE FROM todolists WHERE name = 'My Tasks'"))
