from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Date, func
from sqlalchemy.orm import relationship
from src.models import Base

class WeatherAlert(Base):
    __tablename__ = "weather_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="SET NULL"), nullable=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # severe_weather, unfavorable_conditions, recommendation_change
    severity = Column(String(20), default="info")  # info, warning, severe, critical
    
    # Weather information
    location = Column(String(200), nullable=False)
    alert_date = Column(Date, nullable=False)
    weather_condition = Column(String(100), nullable=False)
    temperature = Column(Float, nullable=True)
    precipitation_chance = Column(Integer, nullable=True)  # percentage
    wind_speed = Column(Float, nullable=True)
    
    # Alert message
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)  # AI-generated suggestions
    alternative_dates = Column(Text, nullable=True)  # Suggested alternative dates
    
    # Status
    is_read = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    
    # Impact assessment
    impact_level = Column(String(20), nullable=True)  # minimal, moderate, significant, critical
    affected_activities = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="weather_alerts")
    itinerary = relationship("Itinerary", backref="weather_alerts")
    destination = relationship("Destination", backref="weather_alerts")
    
    def __repr__(self):
        return f"<WeatherAlert(id={self.id}, type='{self.alert_type}', severity='{self.severity}')>"


class WeatherBasedRecommendation(Base):
    __tablename__ = "weather_based_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="SET NULL"), nullable=True)
    
    # Recommendation context
    recommendation_type = Column(String(50), nullable=False)  # alternative_destination, activity_change, date_change, indoor_alternative
    trigger_condition = Column(String(100), nullable=True)  # what weather condition triggered this
    
    # Weather data
    forecast_date = Column(Date, nullable=False)
    weather_condition = Column(String(100), nullable=False)
    suitability_score = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Recommendation details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=True)
    alternative_suggestion = Column(Text, nullable=True)
    
    # AI context
    confidence_score = Column(Float, nullable=True)
    ai_model_version = Column(String(20), nullable=True)
    
    # User interaction
    is_viewed = Column(Boolean, default=False)
    is_accepted = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    user_feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="weather_recommendations")
    itinerary = relationship("Itinerary", backref="weather_recommendations")
    destination = relationship("Destination", backref="weather_recommendations")
    
    def __repr__(self):
        return f"<WeatherBasedRecommendation(id={self.id}, type='{self.recommendation_type}', score={self.suitability_score})>"
