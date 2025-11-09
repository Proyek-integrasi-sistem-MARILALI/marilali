from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.security import get_current_user
from database.connection import get_db
from database.models import User
from services.favorite_itinerary import controller
from services.favorite_itinerary.schemas import FavoriteItineraryResponse

router = APIRouter()

@router.post("/{itinerary_id}", response_model=FavoriteItineraryResponse)
def add_favorite_itinerary(itinerary_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Tambahkan itinerary ke daftar favorit pengguna.
    """
    return controller.add_favorite_itinerary(current_user.id, itinerary_id, db)


@router.delete("/{itinerary_id}")
def remove_favorite_itinerary(itinerary_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Hapus itinerary dari daftar favorit.
    """
    return controller.remove_favorite_itinerary(current_user.id, itinerary_id, db)


@router.get("/", response_model=list[FavoriteItineraryResponse])
def list_favorite_itineraries(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Lihat semua itinerary favorit pengguna.
    """
    return controller.list_favorite_itineraries(current_user.id, db)
