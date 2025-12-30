from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AccommodationSearchRequest(BaseModel):
    location: str
    check_in: datetime
    check_out: datetime
    guests: int = Field(default=1, ge=1)
    max_price: Optional[int] = None
    min_rating: Optional[float] = Field(default=None, ge=0, le=5)
    amenities: Optional[List[str]] = None
    use_ai_recommendations: bool = Field(default=True, description="Use AI to filter results")


class AccommodationSearchResponse(BaseModel):
    id: int
    location: str
    check_in: datetime
    check_out: datetime
    guests: int
    max_price: Optional[int]
    search_results_count: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


class AccommodationRecommendationResponse(BaseModel):
    id: int
    hotel_name: str
    location: str
    latitude: Optional[float]
    longitude: Optional[float]
    price_per_night: int
    total_price: int
    rating: Optional[float]
    amenities: Optional[List[str]]
    description: Optional[str]
    image_url: Optional[str]
    recommendation_score: float
    recommendation_reason: Optional[str]
    weather_compatible: bool
    budget_compatible: bool
    is_selected: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class AccommodationSelect(BaseModel):
    itinerary_id: int
    accommodation_id: int
