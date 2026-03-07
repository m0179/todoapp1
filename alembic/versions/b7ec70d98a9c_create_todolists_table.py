"""create todolists table

Revision ID: b7ec70d98a9c
Revises: 83fde3aff741
Create Date: 2026-03-06 00:44:13.615507

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7ec70d98a9c'
down_revision: Union[str, Sequence[str], None] = '83fde3aff741'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the todolists table."""
    op.create_table(
        'todolists',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_todolists_id'), 'todolists', ['id'], unique=False)
    op.create_index(op.f('ix_todolists_name'), 'todolists', ['name'], unique=False)
    op.create_index(op.f('ix_todolists_user_id'), 'todolists', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop the todolists table."""
    op.drop_index(op.f('ix_todolists_user_id'), table_name='todolists')
    op.drop_index(op.f('ix_todolists_name'), table_name='todolists')
    op.drop_index(op.f('ix_todolists_id'), table_name='todolists')
    op.drop_table('todolists')
