from sqlalchemy import Column, Integer, String, DateTime, Date, Text, func
from sqlalchemy.orm import relationship
from src.models import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    profile_picture = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    is_verified = Column(Integer, default=0)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    itineraries = relationship("Itinerary", back_populates="user", cascade="all, delete-orphan")
    # preference = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")  # Commented out - UserPreference model not defined
    favorite_destinations = relationship("FavoriteDestination", back_populates="user", cascade="all, delete-orphan")
    favorite_itineraries = relationship("FavoriteItinerary", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
