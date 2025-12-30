from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from src.transportation import service
from src.transportation.schemas import (
    FlightSearchRequest,
    FlightSearchResponse,
    FlightRecommendationResponse,
    FlightSelect
)
from src.auth.security import get_current_user
from src.database import get_db
from src.user.models import User


router = APIRouter()


@router.post("/flights/search", response_model=List[FlightRecommendationResponse])
async def search_flights(
    data: FlightSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.search_flights(current_user.id, data, db)


@router.get("/flights/search-history", response_model=List[FlightSearchResponse])
async def get_search_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_search_history(current_user.id, db)


@router.get("/flights/recommendations", response_model=List[FlightRecommendationResponse])
async def get_recommendations(
    itinerary_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_recommendations(current_user.id, itinerary_id, db)


@router.post("/flights/select", response_model=FlightRecommendationResponse)
async def select_flight(
    data: FlightSelect,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.select_flight(
        current_user.id,
        data.flight_id,
        data.itinerary_id,
        db
    )
