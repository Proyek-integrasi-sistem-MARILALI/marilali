from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.search import service
from src.search.schemas import (
    SearchLogRequest,
    SearchHistoryResponse,
    PopularSearchResponse,
    TrendingSearchResponse,
    SearchAnalyticsResponse,
    SearchSuggestionRequest,
    SearchSuggestionResponse
)
from src.auth.security import get_current_user
from src.database import get_db
from src.user.models import User


router = APIRouter()


@router.post("/log", status_code=status.HTTP_201_CREATED)
async def log_search(
    search_log: SearchLogRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.log_search(
        user_id=current_user.id,
        search_type=search_log.search_type,
        query=search_log.query,
        filters=search_log.filters,
        results_count=search_log.results_count,
        db=db
    )


@router.get("/history", response_model=List[SearchHistoryResponse])
async def get_my_search_history(
    search_type: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_user_search_history(
        user_id=current_user.id,
        search_type=search_type,
        limit=limit,
        db=db
    )


@router.delete("/history", status_code=status.HTTP_200_OK)
async def clear_my_search_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.clear_search_history(
        user_id=current_user.id,
        db=db
    )


@router.get("/popular", response_model=List[PopularSearchResponse])
async def get_popular_searches(
    search_type: str = Query(..., description="destination, itinerary, activity"),
    limit: int = Query(10, ge=1, le=50),
    min_count: int = Query(3, ge=1, description="Minimum search count"),
    db: AsyncSession = Depends(get_db)
):
    return await service.get_popular_searches(
        search_type=search_type,
        limit=limit,
        min_count=min_count,
        db=db
    )


@router.get("/trending", response_model=List[TrendingSearchResponse])
async def get_trending_searches(
    search_type: str = Query(..., description="destination, itinerary, activity"),
    days: int = Query(7, ge=1, le=30, description="Look back period"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    return await service.get_trending_searches(
        search_type=search_type,
        days=days,
        limit=limit,
        db=db
    )


@router.get("/analytics", response_model=SearchAnalyticsResponse)
async def get_my_search_analytics(
    days: int = Query(30, ge=1, le=365, description="Analysis period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_search_analytics(
        user_id=current_user.id,
        days=days,
        db=db
    )


@router.post("/suggestions", response_model=SearchSuggestionResponse)
async def get_search_suggestions(
    request: SearchSuggestionRequest,
    db: AsyncSession = Depends(get_db)
):
    suggestions = await service.get_search_suggestions(
        query=request.query,
        search_type=request.search_type,
        limit=request.limit,
        db=db
    )
    
    return {
        "query": request.query,
        "suggestions": suggestions
    }
