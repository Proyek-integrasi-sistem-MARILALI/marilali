from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Date, func
from sqlalchemy.orm import relationship
from src.models import Base

class Weather(Base):
    __tablename__ = "weather"
    
    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=True, index=True)
    location = Column(String(200), nullable=False)
    date = Column(Date, nullable=False, index=True)
    temperature_min = Column(Float, nullable=True)
    temperature_max = Column(Float, nullable=True)
    temperature_avg = Column(Float, nullable=True)
    condition = Column(String(100), nullable=True)  # sunny, rainy, cloudy, etc.
    humidity = Column(Integer, nullable=True)
    wind_speed = Column(Float, nullable=True)
    precipitation = Column(Float, nullable=True)
    description = Column(String(255), nullable=True)
    icon_code = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    destination = relationship("Destination", backref="weather_records")
    
    def __repr__(self):
        return f"<Weather(id={self.id}, location='{self.location}', date={self.date}, condition='{self.condition}')>"
