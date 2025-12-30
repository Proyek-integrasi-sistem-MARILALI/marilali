"""
Map router for location and route endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.map import service
from src.map.schemas import LocationCreate, LocationResponse, RouteRequest, RouteResponse
from src.auth.security import get_current_user
from src.database import get_db
from src.user.models import User


router = APIRouter()


@router.post("/locations", response_model=LocationResponse)
async def save_location(
    data: LocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save a location for the user."""
    return await service.save_location(current_user.id, data, db)


@router.get("/locations", response_model=List[LocationResponse])
async def get_locations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all saved locations for the user."""
    return await service.get_user_locations(current_user.id, db)


@router.delete("/locations/{location_id}")
async def delete_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a saved location."""
    return await service.delete_location(location_id, current_user.id, db)


@router.post("/route", response_model=RouteResponse)
async def calculate_route(
    data: RouteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate route between two points."""
    return await service.calculate_route(data, db)
