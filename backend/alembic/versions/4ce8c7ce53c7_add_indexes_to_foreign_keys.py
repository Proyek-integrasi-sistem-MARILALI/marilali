"""add_indexes_to_foreign_keys

Revision ID: 4ce8c7ce53c7
Revises: 2b0ce2db97e2
Create Date: 2026-01-05 19:54:12.824093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ce8c7ce53c7'
down_revision: Union[str, None] = '2b0ce2db97e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add indexes to favorite_destinations
    op.create_index('ix_favorite_destinations_user_id', 'favorite_destinations', ['user_id'])
    op.create_index('ix_favorite_destinations_destination_id', 'favorite_destinations', ['destination_id'])
    
    # Add indexes to favorite_itineraries
    op.create_index('ix_favorite_itineraries_user_id', 'favorite_itineraries', ['user_id'])
    op.create_index('ix_favorite_itineraries_itinerary_id', 'favorite_itineraries', ['itinerary_id'])
    
    # Add index to notification itinerary_id (currently missing)
    op.create_index('ix_notifications_itinerary_id', 'notifications', ['itinerary_id'])


def downgrade() -> None:
    # Drop indexes in reverse order
    op.drop_index('ix_notifications_itinerary_id', 'notifications')
    op.drop_index('ix_favorite_itineraries_itinerary_id', 'favorite_itineraries')
    op.drop_index('ix_favorite_itineraries_user_id', 'favorite_itineraries')
    op.drop_index('ix_favorite_destinations_destination_id', 'favorite_destinations')
    op.drop_index('ix_favorite_destinations_user_id', 'favorite_destinations')
