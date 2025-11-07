from pydantic import BaseModel
from typing import Optional, List
from services.review.schemas import ReviewResponse

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
# Schema untuk response destinasi dengan rata-rata rating dan daftar review