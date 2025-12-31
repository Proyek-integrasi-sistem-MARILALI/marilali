from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from src.models import Base

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    title = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)
    visit_date = Column(DateTime(timezone=True), nullable=True)
    would_recommend = Column(Boolean, default=True)
    helpful_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    destination = relationship("Destination", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(id={self.id}, rating={self.rating}, user_id={self.user_id})>"
