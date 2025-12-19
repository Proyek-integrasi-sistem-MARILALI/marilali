from pydantic import BaseModel, Field
from datetime import datetime

class FavoriteDestinationCreate(BaseModel):
    destination_id: int = Field(..., gt=0, example=12)

class FavoriteItineraryCreate(BaseModel):
    itinerary_id: int = Field(..., gt=0, example=5)



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
