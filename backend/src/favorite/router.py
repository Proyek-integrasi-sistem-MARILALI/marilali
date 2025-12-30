from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.favorite import service
from src.favorite.schemas import (
    FavoriteDestinationCreate,
    FavoriteDestinationResponse,
    FavoriteItineraryCreate,
    FavoriteItineraryResponse,
    FavoriteNotesUpdate,
    FavoritesCountResponse
)
from src.auth.security import get_current_user
from src.database import get_db
from src.user.models import User


router = APIRouter()


# Destination favorites
@router.post("/destinations", response_model=FavoriteDestinationResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite_destination(
    favorite: FavoriteDestinationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.add_favorite_destination(
        user_id=current_user.id,
        destination_id=favorite.destination_id,
        notes=favorite.notes,
        db=db
    )


@router.delete("/destinations/{destination_id}", status_code=status.HTTP_200_OK)
async def remove_favorite_destination(
    destination_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.remove_favorite_destination(
        user_id=current_user.id,
        destination_id=destination_id,
        db=db
    )


@router.get("/destinations", response_model=List[FavoriteDestinationResponse])
async def get_favorite_destinations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_favorite_destinations(
        user_id=current_user.id,
        db=db
    )


@router.patch("/destinations/{destination_id}/notes")
async def update_favorite_notes(
    destination_id: int,
    update: FavoriteNotesUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.update_favorite_notes(
        user_id=current_user.id,
        destination_id=destination_id,
        notes=update.notes,
        db=db
    )


@router.get("/destinations/{destination_id}/check")
async def check_is_favorite(
    destination_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    is_favorite = await service.check_is_favorite_destination(
        user_id=current_user.id,
        destination_id=destination_id,
        db=db
    )
    
    return {"is_favorite": is_favorite}


# Itinerary favorites
@router.post("/itineraries", response_model=FavoriteItineraryResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite_itinerary(
    favorite: FavoriteItineraryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.add_favorite_itinerary(
        user_id=current_user.id,
        itinerary_id=favorite.itinerary_id,
        notes=favorite.notes,
        db=db
    )


@router.delete("/itineraries/{itinerary_id}", status_code=status.HTTP_200_OK)
async def remove_favorite_itinerary(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.remove_favorite_itinerary(
        user_id=current_user.id,
        itinerary_id=itinerary_id,
        db=db
    )


@router.get("/itineraries", response_model=List[FavoriteItineraryResponse])
async def get_favorite_itineraries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_favorite_itineraries(
        user_id=current_user.id,
        db=db
    )


@router.get("/count", response_model=FavoritesCountResponse)
async def get_favorites_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_favorites_count(
        user_id=current_user.id,
        db=db
    )
