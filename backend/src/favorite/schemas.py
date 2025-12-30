from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FavoriteDestinationCreate(BaseModel):
    destination_id: int
    notes: Optional[str] = None


class FavoriteDestinationResponse(BaseModel):
    id: int
    user_id: int
    destination_id: int
    notes: Optional[str]
    added_at: datetime
    
    class Config:
        from_attributes = True


class FavoriteItineraryCreate(BaseModel):
    itinerary_id: int
    notes: Optional[str] = None


class FavoriteItineraryResponse(BaseModel):
    id: int
    user_id: int
    itinerary_id: int
    notes: Optional[str]
    added_at: datetime
    
    class Config:
        from_attributes = True


class FavoriteNotesUpdate(BaseModel):
    notes: str = Field(..., min_length=1, max_length=500)


class FavoritesCountResponse(BaseModel):
    destinations: int
    itineraries: int
    total: int
