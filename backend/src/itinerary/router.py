"""
Module: services.itinerary.router
Deskripsi:
Async API endpoints untuk manajemen itinerary perjalanan.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.itinerary import service
from src.itinerary.schemas import ItineraryCreate, ItineraryResponse
from src.auth.security import get_current_user
from src.database import get_db
from src.user.models import User


router = APIRouter()


@router.post("/", response_model=ItineraryResponse)
async def create_itinerary(
    data: ItineraryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new itinerary."""
    return await service.create_itinerary(current_user.id, data, db)


@router.get("/", response_model=list[ItineraryResponse])
async def list_itineraries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all user's itineraries."""
    return await service.get_all_itineraries(current_user.id, db)


@router.get("/history", response_model=list[ItineraryResponse])
async def get_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get completed itineraries (history)."""
    return await service.get_completed_itineraries(current_user.id, db)


@router.get("/{itinerary_id}", response_model=ItineraryResponse)
async def get_itinerary(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific itinerary by ID."""
    return await service.get_itinerary_by_id(itinerary_id, current_user.id, db)


@router.put("/{itinerary_id}/complete", response_model=ItineraryResponse)
async def mark_itinerary_complete(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark itinerary as completed."""
    return await service.mark_itinerary_complete(itinerary_id, current_user.id, db)


@router.post("/{itinerary_id}/copy", response_model=ItineraryResponse)
async def copy_itinerary(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Copy existing itinerary with all details."""
    return await service.copy_itinerary(itinerary_id, current_user.id, db)


@router.put("/{itinerary_id}/share", response_model=ItineraryResponse)
async def share_itinerary_route(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Share itinerary publicly."""
    return await service.share_itinerary(itinerary_id, current_user.id, db)


@router.delete("/{itinerary_id}")
async def delete_itinerary(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete itinerary."""
    return await service.delete_itinerary(itinerary_id, current_user.id, db)
