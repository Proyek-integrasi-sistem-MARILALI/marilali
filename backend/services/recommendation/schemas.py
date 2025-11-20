from pydantic import BaseModel
from typing import Optional

class RecommendationDestinationResponse(BaseModel):
    id: int
    name: str
    category: str
    location: str
    price: Optional[int]
    description: Optional[str]
    image_url: Optional[str]
    average_rating: float = 0.0

    class Config:
        orm_mode = True
