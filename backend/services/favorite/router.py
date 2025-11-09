from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.security import get_current_user
from database.connection import get_db
from database.models import User
from services.favorite import controller
from services.favorite.schemas import FavoriteResponse

router = APIRouter()

@router.post("/{destination_id}", response_model=FavoriteResponse)
def add_favorite(destination_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Tambahkan destinasi ke daftar favorit pengguna.
    """
    return controller.add_favorite(current_user.id, destination_id, db)


@router.delete("/{destination_id}")
def remove_favorite(destination_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Hapus destinasi dari daftar favorit.
    """
    return controller.remove_favorite(current_user.id, destination_id, db)


@router.get("/", response_model=list[FavoriteResponse])
def list_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Lihat semua destinasi favorit pengguna.
    """
    return controller.list_favorites(current_user.id, db)
