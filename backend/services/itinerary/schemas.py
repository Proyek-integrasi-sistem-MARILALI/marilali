from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# ===== Subschemas (dummy dulu, biar kompatibel dengan API pihak ketiga nanti) =====
class FlightSchema(BaseModel):
    airline: Optional[str] = None
    departure_city: Optional[str] = None
    arrival_city: Optional[str] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    price: Optional[int] = None

    class Config:
        orm_mode = True


class AccommodationSchema(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    price_per_night: Optional[int] = None

    class Config:
        orm_mode = True


# ===== Main schemas =====
class ItineraryCreate(BaseModel):
    title: str
    start_date: date
    end_date: date
    budget: Optional[int] = None
    flights: List[FlightSchema] = []
    accommodations: List[AccommodationSchema] = []


class ItineraryResponse(ItineraryCreate):
    id: int
    user_id: int
    created_at: datetime
    status: Optional[str] = "draft"

    class Config:
        orm_mode = True
