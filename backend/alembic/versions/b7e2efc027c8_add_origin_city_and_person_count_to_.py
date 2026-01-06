"""add_origin_city_and_person_count_to_itineraries

Revision ID: b7e2efc027c8
Revises: c70c92118932
Create Date: 2026-01-05 04:27:50.346599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e2efc027c8'
down_revision: Union[str, None] = 'c70c92118932'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add origin_city and person_count columns to itineraries table
    op.add_column('itineraries', sa.Column('origin_city', sa.String(length=100), nullable=True))
    op.add_column('itineraries', sa.Column('person_count', sa.Integer(), nullable=True, server_default='1'))


def downgrade() -> None:
    # Remove origin_city and person_count columns from itineraries table
    op.drop_column('itineraries', 'person_count')
    op.drop_column('itineraries', 'origin_city')
