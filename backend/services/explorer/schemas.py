from pydantic import BaseModel
from typing import Optional, List
from services.review.schemas import ReviewResponse
from datetime import datetime, date

class DestinationBase(BaseModel):
    name: str
    category: str
    location: str
    price: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class DestinationResponse(DestinationBase):
    id: int
    average_rating: Optional[float] = 0.0
    reviews: List[ReviewResponse] = []

    class Config:
        orm_mode = True
        
class PublicItineraryItem(BaseModel):
    id: int
    title: str
    start_date: date
    end_date: date
    budget: Optional[float]
    created_at: datetime

    class Config:
        orm_mode = True

class PublicItineraryResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    budget: Optional[float]
    is_public: bool
    created_at: datetime

    class Config:
        orm_mode = True

class PublicItineraryListResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[PublicItineraryItem]

    class Config:
        orm_mode = True

# Schema untuk response destinasi dengan rata-rata rating dan daftar review