"""
Module: services.review.controller
Deskripsi:
Async business logic untuk review destinasi wisata.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.review.models import Review


async def create_review(user_id: int, review_data, db: AsyncSession):
    """
    Menambahkan review baru oleh pengguna.
    User hanya bisa review satu kali per destinasi.
    """
    # Check if user already reviewed this destination
    result = await db.execute(
        select(Review).where(
            Review.user_id == user_id,
            Review.destination_id == review_data.destination_id
        )
    )
    existing_review = result.scalar_one_or_none()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this destination"
        )

    # Create new review
    review = Review(
        user_id=user_id,
        destination_id=review_data.destination_id,
        rating=review_data.rating,
        comment=review_data.comment,
    )

    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


async def get_reviews_by_destination(destination_id: int, db: AsyncSession):
    """
    Mengambil semua review berdasarkan ID destinasi.
    """
    result = await db.execute(
        select(Review).where(Review.destination_id == destination_id)
    )
    reviews = result.scalars().all()

    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews found for this destination"
        )

    return reviews
