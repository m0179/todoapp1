"""finalize todo todolist relationship

Revision ID: 86f2dc5a531b
Revises: 19da2702fac8
Create Date: 2026-03-06 01:10:57.797535

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86f2dc5a531b'
down_revision: Union[str, Sequence[str], None] = '19da2702fac8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Finalize the todos → todolists relationship:
    - Make todolist_id NOT NULL
    - Add foreign key from todos.todolist_id → todolists.id
    - Remove the old todos.user_id column and its FK/index
    """
    # Make todolist_id NOT NULL (safe: all rows were populated in Migration 3)
    op.alter_column('todos', 'todolist_id', existing_type=sa.Integer(), nullable=False)

    # Add foreign key constraint
    op.create_foreign_key('fk_todos_todolist_id', 'todos', 'todolists', ['todolist_id'], ['id'])

    # Remove the old user_id column and its constraints
    op.drop_constraint('todos_user_id_fkey', 'todos', type_='foreignkey')
    op.drop_index('ix_todos_user_id', table_name='todos')
    op.drop_column('todos', 'user_id')


def downgrade() -> None:
    """Reverse: restore user_id, remove todolist FK, make todolist_id nullable."""
    # Re-add user_id column as nullable first
    op.add_column('todos', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index('ix_todos_user_id', 'todos', ['user_id'], unique=False)

    # Populate user_id from the todolist's owner
    connection = op.get_bind()
    connection.execute(sa.text(
        "UPDATE todos SET user_id = todolists.user_id "
        "FROM todolists WHERE todos.todolist_id = todolists.id"
    ))

    # Make user_id NOT NULL and add FK
    op.alter_column('todos', 'user_id', existing_type=sa.Integer(), nullable=False)
    op.create_foreign_key('todos_user_id_fkey', 'todos', 'users', ['user_id'], ['id'])

    # Remove the todolist FK and make todolist_id nullable again
    op.drop_constraint('fk_todos_todolist_id', 'todos', type_='foreignkey')
    op.alter_column('todos', 'todolist_id', existing_type=sa.Integer(), nullable=True)
