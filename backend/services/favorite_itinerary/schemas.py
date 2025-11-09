from pydantic import BaseModel
from datetime import datetime

class FavoriteItineraryResponse(BaseModel):
    id: int
    itinerary_id: int
    created_at: datetime

    class Config:
        orm_mode = True
