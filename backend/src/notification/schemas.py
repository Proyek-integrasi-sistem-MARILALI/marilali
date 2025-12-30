from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    notification_type: str
    title: str
    message: str
    priority: str = "normal"

class NotificationCreate(NotificationBase):
    user_id: int
    itinerary_id: int | None = None

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    itinerary_id: int | None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
