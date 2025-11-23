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
    is_completed: Optional[bool] = None
    day_number: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    sort_order: Optional[int] = None


class ActivityResponse(BaseModel):
    id: int
    title: str
    location: Optional[str]
    note: Optional[str]
    cost: Optional[int]
    is_completed: bool
    day_number: Optional[int]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    sort_order: int
    created_at: datetime

    class Config:
        orm_mode = True
