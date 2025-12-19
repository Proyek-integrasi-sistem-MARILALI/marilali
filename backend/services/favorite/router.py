from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from services.favorite import controller
from services.favorite.schemas import (
    FavoriteDestinationCreate, FavoriteDestinationResponse,
    FavoriteItineraryCreate, FavoriteItineraryResponse
)

from database.connection import get_db
from core.security import get_current_user
from database.models import User

router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"]
)

# =============================
# FAVORITE DESTINATION ROUTES
# =============================
@router.post(
    "/destinations",
    response_model=FavoriteDestinationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah Favorite Destination"
)
def add_fav_destination(
    data: FavoriteDestinationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.add_favorite_destination(current_user.id, data, db)


@router.delete(
    "/destinations/{destination_id}",
    summary="Hapus Favorite Destination"
)
def remove_fav_destination(
    destination_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.remove_favorite_destination(current_user.id, destination_id, db)


@router.get(
    "/destinations",
    response_model=list[FavoriteDestinationResponse],
    summary="List Favorite Destinations"
)
def list_fav_destinations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.list_favorite_destinations(current_user.id, db)



# =============================
# FAVORITE ITINERARY ROUTES
# =============================
@router.post(
    "/itineraries",
    response_model=FavoriteItineraryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah Favorite Itinerary"
)
def add_fav_itinerary(
    data: FavoriteItineraryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.add_favorite_itinerary(current_user.id, data, db)


@router.delete(
    "/itineraries/{itinerary_id}",
    summary="Hapus Favorite Itinerary"
)
def remove_fav_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.remove_favorite_itinerary(current_user.id, itinerary_id, db)


@router.get(
    "/itineraries",
    response_model=list[FavoriteItineraryResponse],
    summary="List Favorite Itineraries"
)
def list_fav_itineraries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.list_favorite_itineraries(current_user.id, db)
