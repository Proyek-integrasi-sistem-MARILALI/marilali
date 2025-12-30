from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from src.accommodation import service
from src.accommodation.schemas import (
    AccommodationSearchRequest,
    AccommodationSearchResponse,
    AccommodationRecommendationResponse,
    AccommodationSelect
)
from src.auth.security import get_current_user
from src.database import get_db
from src.user.models import User


router = APIRouter()


@router.post("/search", response_model=List[AccommodationRecommendationResponse])
async def search_accommodations(
    data: AccommodationSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.search_accommodations(current_user.id, data, db)


@router.get("/search-history", response_model=List[AccommodationSearchResponse])
async def get_search_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_search_history(current_user.id, db)


@router.get("/recommendations", response_model=List[AccommodationRecommendationResponse])
async def get_recommendations(
    itinerary_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_recommendations(current_user.id, itinerary_id, db)


@router.post("/select", response_model=AccommodationRecommendationResponse)
async def select_accommodation(
    data: AccommodationSelect,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.select_accommodation(
        current_user.id,
        data.accommodation_id,
        data.itinerary_id,
        db
    )
