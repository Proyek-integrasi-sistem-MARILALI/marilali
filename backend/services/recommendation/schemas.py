from pydantic import BaseModel
from typing import List, Optional

class RecommendationRequest(BaseModel):
    location_area: str
    preferred_categories: List[str] = []
    max_budget: int
    include_flight: bool = False
    include_accommodation: bool = True

class RecommendedDestination(BaseModel):
    id: int
    name: str
    category: str
    location: str
    price: Optional[int]
    image_url: Optional[str]
    rating: float
    estimated_cost: int

    class Config:
        orm_mode = True

class RecommendationResponse(BaseModel):
    total_min_cost: int
    destinations: List[RecommendedDestination]
