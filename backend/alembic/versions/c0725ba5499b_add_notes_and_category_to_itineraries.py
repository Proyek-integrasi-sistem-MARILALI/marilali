"""Add notes and category to itineraries

Revision ID: c0725ba5499b
Revises: 4ce8c7ce53c7
Create Date: 2026-01-06 02:37:49.356356

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c0725ba5499b'
down_revision: Union[str, None] = '4ce8c7ce53c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add notes column to itineraries table
    op.add_column('itineraries', sa.Column('notes', sa.Text(), nullable=True))
    
    # Modify category column length from VARCHAR(50) to VARCHAR(100)
    op.alter_column('itineraries', 'category',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=100),
               existing_nullable=True)


def downgrade() -> None:
    # Revert category column length back to VARCHAR(50)
    op.alter_column('itineraries', 'category',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)
    
    # Drop notes column
    op.drop_column('itineraries', 'notes')
