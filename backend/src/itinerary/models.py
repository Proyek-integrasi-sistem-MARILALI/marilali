from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from src.models import Base

class Itinerary(Base):
    __tablename__ = "itineraries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    destination_country = Column(String(100), nullable=True)
    destination_city = Column(String(100), nullable=True)
    origin_city = Column(String(100), nullable=True)  # Added for trip display
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Integer, nullable=True)
    actual_cost = Column(Integer, nullable=True)
    currency = Column(String(10), default="USD")
    person_count = Column(Integer, default=1)  # Number of travelers
    notes = Column(Text, nullable=True)  # Additional notes/description
    category = Column(String(100), nullable=True)  # Category like "WaterSport", "Culture", "Nature"
    status = Column(String(50), default="planned", index=True)  # planned, ongoing, completed, cancelled
    is_public = Column(Boolean, default=False, index=True)
    is_template = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    copy_count = Column(Integer, default=0)
    thumbnail_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="itineraries")
    flights = relationship("Flight", back_populates="itinerary", cascade="all, delete-orphan")
    accommodations = relationship("Accommodation", back_populates="itinerary", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="itinerary", cascade="all, delete-orphan")
    # checklists = relationship("Checklist", back_populates="itinerary", cascade="all, delete-orphan")  # Checklist model not defined
    expenses = relationship("Expense", back_populates="itinerary", cascade="all, delete-orphan")
    favorite_itineraries = relationship("FavoriteItinerary", back_populates="itinerary", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Itinerary(id={self.id}, title='{self.title}', user_id={self.user_id})>"


class Accommodation(Base):
    __tablename__ = "accommodations"
    
    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=True)
    location = Column(String(150), nullable=True)
    check_in = Column(DateTime(timezone=True), nullable=True)
    check_out = Column(DateTime(timezone=True), nullable=True)
    price_per_night = Column(Integer, nullable=True)
    total_price = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    itinerary = relationship("Itinerary", back_populates="accommodations")
    
    def __repr__(self):
        return f"<Accommodation(id={self.id}, name='{self.name}', itinerary_id={self.itinerary_id})>"


class Flight(Base):
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False, index=True)
    airline = Column(String(100), nullable=True)
    flight_number = Column(String(20), nullable=True)
    departure_city = Column(String(100), nullable=True)
    arrival_city = Column(String(100), nullable=True)
    departure_time = Column(DateTime(timezone=True), nullable=True)
    arrival_time = Column(DateTime(timezone=True), nullable=True)
    price = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    itinerary = relationship("Itinerary", back_populates="flights")
    
    def __repr__(self):
        return f"<Flight(id={self.id}, airline='{self.airline}', itinerary_id={self.itinerary_id})>"


class Transportation(Base):
    __tablename__ = "transportations"
    
    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False, index=True)
    transport_type = Column(String(50), nullable=False)  # car, bus, train, flight, boat, etc.
    from_location = Column(String(200), nullable=False)
    to_location = Column(String(200), nullable=False)
    departure_time = Column(DateTime(timezone=True), nullable=True)
    arrival_time = Column(DateTime(timezone=True), nullable=True)
    provider = Column(String(150), nullable=True)  # airline, bus company, etc.
    cost = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    itinerary = relationship("Itinerary", backref="transportations")
    
    def __repr__(self):
        return f"<Transportation(id={self.id}, type='{self.transport_type}', {self.from_location}->{self.to_location})>"

