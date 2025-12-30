from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func, JSON
from sqlalchemy.orm import relationship
from src.models import Base


class SavedLocation(Base):
    __tablename__ = "saved_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    address = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    place_type = Column(String(50), nullable=True)  # hotel, restaurant, attraction, etc.
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="saved_locations")
    
    def __repr__(self):
        return f"<SavedLocation(id={self.id}, name='{self.name}')>"


class RouteCache(Base):
    __tablename__ = "route_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    destination_lat = Column(Float, nullable=False)
    destination_lng = Column(Float, nullable=False)
    transport_mode = Column(String(50), nullable=False)  # driving, walking, transit
    route_data = Column(JSON, nullable=False)  # stores route geometry, duration, distance
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<RouteCache(id={self.id}, mode='{self.transport_mode}')>"
