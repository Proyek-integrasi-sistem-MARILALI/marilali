from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date, datetime


class WeatherForecastResponse(BaseModel):
    location: str
    current_temp: float
    condition: str
    description: Optional[str]
    humidity: Optional[int]
    wind_speed: Optional[float]
    forecast: List[Dict]
    source: Optional[str] = "api"


class WeatherAlertCreate(BaseModel):
    destination_id: int
    alert_type: str = Field(..., description="temperature_high, temperature_low, rain, storm")
    threshold_value: float = Field(..., description="Threshold value for alert")


class WeatherAlertResponse(BaseModel):
    id: int
    user_id: int
    destination_id: int
    alert_type: str
    threshold_value: float
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class WeatherRecommendationRequest(BaseModel):
    destination_id: int
    travel_date: date


class WeatherRecommendationResponse(BaseModel):
    destination_id: int
    travel_date: date
    recommendations: List[str]
