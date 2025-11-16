from pydantic import BaseModel
from datetime import datetime

class FavoriteDestinationCreate(BaseModel):
    destination_id: int

class FavoriteItineraryCreate(BaseModel):
    itinerary_id: int


class FavoriteDestinationResponse(BaseModel):
    id: int
    destination_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class FavoriteItineraryResponse(BaseModel):
    id: int
    itinerary_id: int
    created_at: datetime

    class Config:
        orm_mode = True
