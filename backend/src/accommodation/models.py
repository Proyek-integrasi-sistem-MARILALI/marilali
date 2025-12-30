from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON, func
from sqlalchemy.orm import relationship
from src.models import Base


class AccommodationSearch(Base):
    __tablename__ = "accommodation_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    location = Column(String(200), nullable=False)
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)
    guests = Column(Integer, default=1)
    max_price = Column(Integer, nullable=True)
    min_rating = Column(Float, nullable=True)
    amenities = Column(JSON, nullable=True)  # ["wifi", "pool", "parking"]
    search_results_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="accommodation_searches")
    
    def __repr__(self):
        return f"<AccommodationSearch(id={self.id}, location='{self.location}')>"


class AccommodationRecommendation(Base):
    __tablename__ = "accommodation_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=True, index=True)
    hotel_name = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    price_per_night = Column(Integer, nullable=False)
    total_price = Column(Integer, nullable=False)
    rating = Column(Float, nullable=True)
    amenities = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    recommendation_score = Column(Float, default=0.0)  # AI confidence score
    recommendation_reason = Column(Text, nullable=True)  # Why AI recommended this
    weather_compatible = Column(Boolean, default=True)
    budget_compatible = Column(Boolean, default=True)
    is_selected = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="accommodation_recommendations")
    itinerary = relationship("Itinerary", backref="accommodation_recommendations")
    
    def __repr__(self):
        return f"<AccommodationRecommendation(id={self.id}, hotel='{self.hotel_name}')>"
