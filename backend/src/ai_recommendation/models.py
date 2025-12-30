from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from src.models import Base


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=True)
    session_id = Column(Integer, ForeignKey("recommendation_sessions.id", ondelete="CASCADE"), nullable=True)
    recommendation_type = Column(String(50), nullable=False)  # destination, itinerary, activity
    confidence_score = Column(Float, nullable=False, default=0.0)
    reasoning = Column(JSON, nullable=True)  
    user_rating = Column(Integer, nullable=True)  # User feedback 1-5
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    destination = relationship("Destination")
    session = relationship("RecommendationSession", back_populates="recommendations")


class RecommendationSession(Base):
    __tablename__ = "recommendation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_type = Column(String(50), nullable=False)
    filters = Column(JSON, nullable=True)  # User's search filters
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    recommendations = relationship("AIRecommendation", back_populates="session")
