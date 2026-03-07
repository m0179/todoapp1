"""add todolist_id to todos table

Revision ID: 51a5b079280f
Revises: b7ec70d98a9c
Create Date: 2026-03-06 00:47:06.864098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51a5b079280f'
down_revision: Union[str, Sequence[str], None] = 'b7ec70d98a9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add todolist_id column to todos table as nullable.

    Kept nullable so we can populate it with data before enforcing NOT NULL.
    user_id is preserved here — it will be removed in a later migration
    after data migration is complete.
    """
    op.add_column('todos', sa.Column('todolist_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_todos_todolist_id'), 'todos', ['todolist_id'], unique=False)


def downgrade() -> None:
    """Remove todolist_id column from todos table."""
    op.drop_index(op.f('ix_todos_todolist_id'), table_name='todos')
    op.drop_column('todos', 'todolist_id')
