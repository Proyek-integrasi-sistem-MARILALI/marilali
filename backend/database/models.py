"""
Module: database.models
Deskripsi:
Berisi definisi model ORM untuk tabel dalam database.
Model ini digunakan oleh SQLAlchemy untuk membuat dan mengelola tabel secara otomatis.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base


class User(Base):
    """
    Model User merepresentasikan data pengguna dalam sistem Travel Planner.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relasi ke Review
    reviews = relationship("Review", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Destination(Base):
    """
    Model Destination menyimpan data destinasi wisata.
    """
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    location = Column(String(150), nullable=False)
    price = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relasi ke Review
    reviews = relationship("Review", backref="destination", cascade="all, delete")

    def __repr__(self):
        return f"<Destination(id={self.id}, name={self.name})>"


class Review(Base):
    """
    Model Review menyimpan ulasan pengguna terhadap destinasi wisata.
    """
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"))
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relasi balik ke User
    user = relationship("User", back_populates="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, rating={self.rating}, user_id={self.user_id})>"
    

class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Integer, nullable=True)
    status = Column(String, default="planned")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="itineraries")
    flights = relationship("Flight", back_populates="itinerary", cascade="all, delete-orphan")
    accommodations = relationship("Accommodation", back_populates="itinerary", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Itinerary(id={self.id}, title='{self.title}', user_id={self.user_id})>"

class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"))
    airline = Column(String)
    departure_city = Column(String)
    arrival_city = Column(String)
    departure_time = Column(DateTime)
    arrival_time = Column(DateTime)
    price = Column(Integer)

    itinerary = relationship("Itinerary", back_populates="flights")
    
    def __repr__(self):
        return f"<Flight(id={self.id}, airline='{self.airline}', from='{self.departure_city}', to='{self.arrival_city}')>"
     
    
class Accommodation(Base):
    __tablename__ = "accommodations"

    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"))
    name = Column(String)
    location = Column(String)
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    price_per_night = Column(Integer)

    itinerary = relationship("Itinerary", back_populates="accommodations")
    
    def __repr__(self):
        return f"<Accommodation(id={self.id}, name='{self.name}', location='{self.location}')>"
    
class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    preferred_category = Column(String, nullable=True)
    min_budget = Column(Integer, nullable=True)
    max_budget = Column(Integer, nullable=True)
    weather_preference = Column(String, nullable=True)

    user = relationship("User", backref="preference")

class FavoriteDestination(Base):
    __tablename__ = "favorite_destinations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="favorite_destinations")
    destination = relationship("Destination")

class FavoriteItinerary(Base):
    __tablename__ = "favorite_itineraries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="favorite_itineraries")
    itinerary = relationship("Itinerary")

# Membuat semua tabel di database