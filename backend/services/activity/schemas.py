from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ActivityCreate(BaseModel):
    destination_id: int
    itinerary_id: int

class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    note: Optional[str] = None
    cost: Optional[int] = None

class ActivityResponse(BaseModel):
    id: int
    title: str
    location: Optional[str]
    note: Optional[str]
    cost: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True
