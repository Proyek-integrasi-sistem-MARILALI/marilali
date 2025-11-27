from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ActivityCreate(BaseModel):
    destination_id: int
    itinerary_id: int
    day_number: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    sort_order: Optional[int] = 0


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    note: Optional[str] = None
    cost: Optional[int] = None

    # 🔥 NEW FIELDS
    day_number: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    sort_order: Optional[int] = None
    is_completed: Optional[bool] = None


class ActivityResponse(BaseModel):
    id: int
    title: str
    location: Optional[str]
    note: Optional[str]
    cost: Optional[int]
    created_at: datetime

    # 🔥 NEW FIELDS
    day_number: Optional[int]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    sort_order: int
    is_completed: bool

    class Config:
        orm_mode = True


class ActivityCreateManual(BaseModel):
    itinerary_id: int
    title: str
    location: Optional[str] = None
    note: Optional[str] = None
    cost: Optional[int] = None
    day_number: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    sort_order: Optional[int] = 0


class ActivityOrderUpdate(BaseModel):
    activity_id: int
    sort_order: int


class ActivityReorderRequest(BaseModel):
    items: list[ActivityOrderUpdate]
