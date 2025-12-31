"""
Module: services.itinerary.schemas
Deskripsi:
Pydantic v2 schemas untuk itinerary, flights, dan accommodations.
"""

from pydantic import ConfigDict
from typing import Optional, List
from datetime import date, datetime
from src.schemas import CustomModel


class FlightSchema(CustomModel):
    """Schema untuk flight information."""
    id: Optional[int] = None
    airline: Optional[str] = None
    departure_city: Optional[str] = None
    arrival_city: Optional[str] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    price: Optional[int] = None


class AccommodationSchema(CustomModel):
    """Schema untuk accommodation information."""
    id: Optional[int] = None
    name: Optional[str] = None
    location: Optional[str] = None
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    price_per_night: Optional[int] = None


class ItineraryCreate(CustomModel):
    """Schema untuk membuat itinerary baru."""
    title: str
    start_date: date
    end_date: date
    budget: Optional[int] = None
    flights: List[FlightSchema] = []
    accommodations: List[AccommodationSchema] = []


class ItineraryResponse(CustomModel):
    """Schema untuk response itinerary."""
    id: int
    user_id: int
    title: str
    start_date: date
    end_date: date
    budget: Optional[int] = None
    status: Optional[str] = "planned"
    is_public: bool = False
    created_at: datetime
    flights: List[FlightSchema] = []
    accommodations: List[AccommodationSchema] = []


class ItineraryShareResponse(CustomModel):
    """Schema untuk response setelah share itinerary."""
    id: int
    is_public: bool
