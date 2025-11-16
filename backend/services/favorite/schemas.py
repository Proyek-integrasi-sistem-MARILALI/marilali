from pydantic import BaseModel
from datetime import datetime

# ========== CREATE REQUEST ==========
class FavoriteDestinationCreate(BaseModel):
    destination_id: int

class FavoriteItineraryCreate(BaseModel):
    itinerary_id: int


# ========== RESPONSE SCHEMA ==========
class FavoriteDestinationResponse(BaseModel):
    id: int
    user_id: int
    destination_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class FavoriteItineraryResponse(BaseModel):
    id: int
    user_id: int
    itinerary_id: int
    created_at: datetime

    class Config:
        orm_mode = True
