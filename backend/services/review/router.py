"""
Module: services.review.router
Deskripsi:
Menyediakan endpoint untuk fitur ulasan destinasi wisata,
termasuk membuat dan mengambil review berdasarkan destinasi.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from services.review import controller
from services.review.schemas import ReviewCreate, ReviewResponse
from database.connection import get_db
from core.security import get_current_user
from database.models import User

# Inisialisasi router untuk modul review
router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah review destinasi",
    description="Menambahkan ulasan baru untuk destinasi tertentu. Hanya pengguna login yang dapat menambahkan ulasan."
)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint untuk menambah review baru.
    """
    return controller.create_review(user_id=current_user.id, review_data=review, db=db)


@router.get(
    "/{destination_id}",
    response_model=list[ReviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Ambil review destinasi",
    description="Mengambil semua ulasan berdasarkan ID destinasi wisata."
)
def get_reviews(destination_id: int, db: Session = Depends(get_db)):
    """
    Endpoint untuk mengambil semua review dari destinasi tertentu.
    """
    return controller.get_reviews_by_destination(destination_id, db)
