"""
Module: services.review.controller
Deskripsi:
Berisi logika bisnis untuk fitur review destinasi wisata,
termasuk pembuatan dan pengambilan ulasan pengguna.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import Review


def create_review(user_id: int, review_data, db: Session):
    """
    Menambahkan review baru oleh pengguna.
    """
    # Cek apakah user sudah pernah review destinasi yang sama
    existing_review = (
        db.query(Review)
        .filter(Review.user_id == user_id, Review.destination_id == review_data.destination_id)
        .first()
    )
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kamu sudah memberikan review untuk destinasi ini."
        )

    # Buat review baru
    review = Review(
        user_id=user_id,
        destination_id=review_data.destination_id,
        rating=review_data.rating,
        comment=review_data.comment,
    )

    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews_by_destination(destination_id: int, db: Session):
    """
    Mengambil semua review berdasarkan ID destinasi.
    """
    reviews = db.query(Review).filter(Review.destination_id == destination_id).all()

    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Belum ada ulasan untuk destinasi ini."
        )

    return reviews
