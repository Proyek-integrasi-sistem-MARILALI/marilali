"""
Module: database.models
Deskripsi:
Berisi definisi model ORM untuk tabel dalam database.
"""

from sqlalchemy import (
    Column, Integer, String, ForeignKey, Text, Date, DateTime, Boolean, func
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base


# ==========================
#        USER
# ==========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    reviews = relationship("Review", back_populates="user", cascade="all, delete")
    preference = relationship("UserPreference", uselist=False, back_populates="user", cascade="all, delete")
    itineraries = relationship("Itinerary", back_populates="user", cascade="all, delete")
    favorite_destinations = relationship("FavoriteDestination", back_populates="user", cascade="all, delete")
    favorite_itineraries = relationship("FavoriteItinerary", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


# ==========================
#     DESTINATION
# ==========================
class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    location = Column(String(150), nullable=False)
    price = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    reviews = relationship("Review", back_populates="destination", cascade="all, delete")
    favored_by = relationship("FavoriteDestination", back_populates="destination", cascade="all, delete")

    def __repr__(self):
        return f"<Destination(id={self.id}, name={self.name})>"


# ==========================
#         REVIEW
# ==========================
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"))
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    user = relationship("User", back_populates="reviews")
    destination = relationship("Destination", back_populates="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, rating={self.rating})>"


# ==========================
#        ITINERARY
# ==========================
class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Integer, nullable=True)
    status = Column(String, default="planned")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_public = Column(Boolean, default=False)

    # Relations
    user = relationship("User", back_populates="itineraries")
    flights = relationship("Flight", back_populates="itinerary", cascade="all, delete-orphan")
    accommodations = relationship("Accommodation", back_populates="itinerary", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="itinerary", cascade="all, delete-orphan")
    favored_by = relationship("FavoriteItinerary", back_populates="itinerary", cascade="all, delete")

    def __repr__(self):
        return f"<Itinerary(id={self.id}, title='{self.title}')>"


# ==========================
#         FLIGHT
# ==========================
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
        return f"<Flight(id={self.id}, airline='{self.airline}')>"


# ==========================
#       ACCOMMODATION
# ==========================
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
        return f"<Accommodation(id={self.id}, name='{self.name}')>"


# ==========================
#     USER PREFERENCE
# ==========================
class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    preferred_category = Column(String, nullable=True)
    min_budget = Column(Integer, nullable=True)
    max_budget = Column(Integer, nullable=True)
    weather_preference = Column(String, nullable=True)

    user = relationship("User", back_populates="preference")


# ==========================
#   FAVORITE DESTINATION
# ==========================
class FavoriteDestination(Base):
    __tablename__ = "favorite_destinations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="favorite_destinations")
    destination = relationship("Destination", back_populates="favored_by")


# ==========================
#   FAVORITE ITINERARY
# ==========================
class FavoriteItinerary(Base):
    __tablename__ = "favorite_itineraries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="favorite_itineraries")
    itinerary = relationship("Itinerary", back_populates="favored_by")


# ==========================
#         ACTIVITY
# ==========================
class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    location = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    cost = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 🔥 NEW FIELDS
    day_number = Column(Integer, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    sort_order = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)

    itinerary = relationship("Itinerary", backref="activities")

