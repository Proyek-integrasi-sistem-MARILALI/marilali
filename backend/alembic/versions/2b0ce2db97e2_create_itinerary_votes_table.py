"""create_itinerary_votes_table

Revision ID: 2b0ce2db97e2
Revises: b7e2efc027c8
Create Date: 2026-01-05 19:36:50.137414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b0ce2db97e2'
down_revision: Union[str, None] = 'b7e2efc027c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create itinerary_votes table
    op.create_table(
        'itinerary_votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('itinerary_id', sa.Integer(), nullable=False),
        sa.Column('vote_type', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['itinerary_id'], ['itineraries.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'itinerary_id', name='user_itinerary_vote_unique'),
        sa.CheckConstraint("vote_type IN ('upvote', 'downvote')", name='vote_type_check')
    )
    
    # Create indexes for performance
    op.create_index('ix_itinerary_votes_user_id', 'itinerary_votes', ['user_id'])
    op.create_index('ix_itinerary_votes_itinerary_id', 'itinerary_votes', ['itinerary_id'])
    
    # Add category column to itineraries table
    op.add_column('itineraries', sa.Column('category', sa.String(length=50), nullable=True))
    op.create_index('ix_itineraries_category', 'itineraries', ['category'])


def downgrade() -> None:
    # Remove category column from itineraries
    op.drop_index('ix_itineraries_category', table_name='itineraries')
    op.drop_column('itineraries', 'category')
    
    # Drop indexes
    op.drop_index('ix_itinerary_votes_itinerary_id', table_name='itinerary_votes')
    op.drop_index('ix_itinerary_votes_user_id', table_name='itinerary_votes')
    
    # Drop table
    op.drop_table('itinerary_votes')
