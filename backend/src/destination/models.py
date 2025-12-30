from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, func, JSON, Table
from sqlalchemy.orm import relationship
from src.models import Base

class Destination(Base):
    __tablename__ = "destinations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    location = Column(String(150), nullable=False)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    price = Column(Integer, nullable=True)
    rating = Column(Float, default=0.0, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    opening_hours = Column(String(255), nullable=True)
    contact_info = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Data Provenance (for OpenDataBay + OpenStreetMap integration)
    source = Column(String(50), default="manual", nullable=False, index=True)  
    # Values: "opendatabay", "openstreetmap", "opendatabay+openstreetmap", "manual"
    
    osm_id = Column(String(50), nullable=True, index=True)  # OpenStreetMap ID
    osm_type = Column(String(20), nullable=True)  # node, way, relation
    osm_tags = Column(JSON, nullable=True)  # Raw OSM tags
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reviews = relationship("Review", back_populates="destination", cascade="all, delete-orphan")
    favorite_destinations = relationship("FavoriteDestination", back_populates="destination", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Destination(id={self.id}, name='{self.name}')>"
