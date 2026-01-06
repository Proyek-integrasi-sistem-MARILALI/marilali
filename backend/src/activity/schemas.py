from pydantic import Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from src.schemas import CustomModel
from src.destination.schemas import DestinationResponse


class ActivityBase(CustomModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    activity_date: date
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    estimated_cost: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class ActivityCreate(ActivityBase):
    destination_id: Optional[int] = None
    order_index: int = Field(default=0, ge=0)


class ActivityUpdate(CustomModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    activity_date: Optional[date] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    estimated_cost: Optional[int] = Field(None, ge=0)
    actual_cost: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    is_completed: Optional[bool] = None
    order_index: Optional[int] = Field(None, ge=0)


class ActivityReorder(CustomModel):
    activity_id: int
    new_order_index: int = Field(..., ge=0)


class ActivityBulkReorder(CustomModel):
    activities: list[ActivityReorder]


class ActivityResponse(ActivityBase):
    id: int
    itinerary_id: int
    destination_id: Optional[int] = None
    destination: Optional[DestinationResponse] = None
    actual_cost: Optional[int] = None
    order_index: int
    is_completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityWithDestination(ActivityResponse):
    destination_name: Optional[str] = None
    destination_category: Optional[str] = None
