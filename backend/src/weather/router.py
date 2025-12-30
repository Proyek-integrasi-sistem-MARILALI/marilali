from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from src.weather import service
from src.weather.schemas import (
    WeatherForecastResponse,
    WeatherAlertCreate,
    WeatherAlertResponse,
    WeatherRecommendationRequest,
    WeatherRecommendationResponse
)
from src.auth.security import get_current_user
from src.database import get_db
from src.user.models import User


router = APIRouter()


@router.get("/forecast", response_model=WeatherForecastResponse)
async def get_weather_forecast(
    location: str = Query(..., description="Location name or coordinates"),
    destination_id: Optional[int] = Query(None, description="Destination ID"),
    days: int = Query(7, ge=1, le=14, description="Number of days"),
    db: AsyncSession = Depends(get_db)
):
    return await service.get_weather_forecast(
        location=location,
        destination_id=destination_id,
        days=days,
        db=db
    )


@router.post("/alerts", response_model=WeatherAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_weather_alert(
    alert: WeatherAlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.create_weather_alert(
        user_id=current_user.id,
        destination_id=alert.destination_id,
        alert_type=alert.alert_type,
        threshold_value=alert.threshold_value,
        db=db
    )


@router.get("/alerts", response_model=List[WeatherAlertResponse])
async def get_my_weather_alerts(
    active_only: bool = Query(True, description="Only show active alerts"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_user_weather_alerts(
        user_id=current_user.id,
        db=db,
        active_only=active_only
    )


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_200_OK)
async def delete_weather_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.delete_weather_alert(
        alert_id=alert_id,
        user_id=current_user.id,
        db=db
    )


@router.post("/recommendations", response_model=WeatherRecommendationResponse)
async def get_weather_recommendations(
    request: WeatherRecommendationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recommendations = await service.get_weather_based_recommendations(
        destination_id=request.destination_id,
        travel_date=request.travel_date,
        db=db
    )
    
    return {
        "destination_id": request.destination_id,
        "travel_date": request.travel_date,
        "recommendations": recommendations
    }
