from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FlightSearchRequest(BaseModel):
    origin: str = Field(description="Origin city or airport code")
    destination: str = Field(description="Destination city or airport code")
    departure_date: datetime
    return_date: Optional[datetime] = None
    passengers: int = Field(default=1, ge=1, le=9)
    cabin_class: str = Field(default="economy", description="economy, business, first")
    max_price: Optional[int] = None
    use_ai_recommendations: bool = Field(default=True, description="Use AI to optimize results")


class FlightSearchResponse(BaseModel):
    id: int
    origin: str
    destination: str
    departure_date: datetime
    return_date: Optional[datetime]
    passengers: int
    cabin_class: str
    max_price: Optional[int]
    search_results_count: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


class FlightRecommendationResponse(BaseModel):
    id: int
    airline: str
    flight_number: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    stops: int
    cabin_class: str
    price: int
    baggage_allowance: Optional[str]
    recommendation_score: float
    recommendation_reason: Optional[str]
    budget_compatible: bool
    weather_optimized: bool
    is_selected: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class FlightSelect(BaseModel):
    itinerary_id: int
    flight_id: int
