from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON, func
from sqlalchemy.orm import relationship
from src.models import Base


class FlightSearch(Base):
    __tablename__ = "flight_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    departure_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=True)
    passengers = Column(Integer, default=1)
    cabin_class = Column(String(50), default="economy")
    max_price = Column(Integer, nullable=True)
    search_results_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="flight_searches")
    
    def __repr__(self):
        return f"<FlightSearch(id={self.id}, {self.origin}->{self.destination})>"


class FlightRecommendation(Base):
    __tablename__ = "flight_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=True, index=True)
    airline = Column(String(100), nullable=False)
    flight_number = Column(String(20), nullable=False)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    stops = Column(Integer, default=0)
    cabin_class = Column(String(50), default="economy")
    price = Column(Integer, nullable=False)
    baggage_allowance = Column(String(100), nullable=True)
    recommendation_score = Column(Float, default=0.0)
    recommendation_reason = Column(Text, nullable=True)
    budget_compatible = Column(Boolean, default=True)
    weather_optimized = Column(Boolean, default=True)
    is_selected = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="flight_recommendations")
    itinerary = relationship("Itinerary", backref="flight_recommendations")
    
    def __repr__(self):
        return f"<FlightRecommendation(id={self.id}, flight='{self.flight_number}')>"
