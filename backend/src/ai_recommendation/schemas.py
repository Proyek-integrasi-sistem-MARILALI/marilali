from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date, datetime


class RecommendationRequest(BaseModel):
    budget_min: Optional[float] = Field(None, ge=0, description="Minimum budget in Indonesian Rupiah (IDR)")
    budget_max: Optional[float] = Field(None, ge=0, description="Maximum budget in Indonesian Rupiah (IDR)")
    start_date: Optional[date] = Field(None, description="Travel start date")
    end_date: Optional[date] = Field(None, description="Travel end date")
    preferences: Optional[List[str]] = Field(None, description="Preferred categories")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Number of recommendations")


class RecommendationResponse(BaseModel):
    id: int
    destination_id: int
    recommendation_type: str
    confidence_score: float
    reasoning: Dict  # Changed from str to Dict to hold detailed reasoning (includes weather_context)
    created_at: datetime
    
    # Nested destination data
    destination: Optional[Dict] = None
    
    # Note: weather_context is now inside reasoning object, not duplicated at top level
    
    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    recommendation_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    feedback_text: Optional[str] = Field(None, max_length=500)


class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    recommendation_id: int
    rating: int
    feedback_text: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ItinerarySuggestionRequest(BaseModel):
    destination_id: int
    days: int = Field(..., ge=1, le=30, description="Number of days")
    budget: float = Field(..., ge=0, description="Total budget in Indonesian Rupiah (IDR)")


class ItinerarySuggestionResponse(BaseModel):
    destination: Dict
    duration_days: int
    total_budget: float
    budget_per_day: float
    currency: str = "IDR"
    suggested_allocation: Dict
    suggested_activities: List[Dict]
    tips: List[str]
