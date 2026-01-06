from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, func
from sqlalchemy.orm import relationship
from src.models import Base

class ItineraryVote(Base):
    __tablename__ = "itinerary_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False, index=True)
    vote_type = Column(String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="itinerary_votes")
    itinerary = relationship("Itinerary", backref="votes")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'itinerary_id', name='user_itinerary_vote_unique'),
        CheckConstraint("vote_type IN ('upvote', 'downvote')", name='vote_type_check'),
    )
    
    def __repr__(self):
        return f"<ItineraryVote(user_id={self.user_id}, itinerary_id={self.itinerary_id}, vote_type={self.vote_type})>"
