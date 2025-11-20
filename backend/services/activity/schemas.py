from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ActivityCreate(BaseModel):
    destination_id: int
    itinerary_id: int

class ActivityResponse(BaseModel):
    id: int
    title: str
    location: Optional[str]
    note: Optional[str]
    cost: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True
