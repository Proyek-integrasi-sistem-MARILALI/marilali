from pydantic import BaseModel
from typing import Optional, List

class PlannerInput(BaseModel):
    location: str
    category: Optional[str] = None
    budget: int
    weather_preference: Optional[str] = "sunny"  # sunny | cloudy | rainy

class PlannerRecommendationItem(BaseModel):
    destination_id: int
    name: str
    category: str
    location: str
    price: int
    rating: float
    weather_suitability: str

class PlannerRecommendationResponse(BaseModel):
    recommendations: List[PlannerRecommendationItem]
