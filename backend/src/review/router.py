"""
Module: services.review.router
Deskripsi:
Async API endpoints untuk ulasan destinasi wisata.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.review import service
from src.review.schemas import ReviewCreate, ReviewResponse
from src.database import get_db
from src.auth.security import get_current_user
from src.user.models import User


router = APIRouter()


@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create destination review",
    description="Add a new review for a destination. User can only review once per destination."
)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint untuk menambah review baru."""
    return await service.create_review(user_id=current_user.id, review_data=review, db=db)


@router.get(
    "/{destination_id}",
    response_model=list[ReviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Get destination reviews",
    description="Retrieve all reviews for a specific destination."
)
async def get_reviews(destination_id: int, db: AsyncSession = Depends(get_db)):
    """Endpoint untuk mengambil semua review dari destinasi tertentu."""
    return await service.get_reviews_by_destination(destination_id, db)
