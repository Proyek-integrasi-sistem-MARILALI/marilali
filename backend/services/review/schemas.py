"""
Module: services.review.schemas
Deskripsi:
Schema (Pydantic models) untuk validasi input dan output data ulasan (review) destinasi wisata.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    """
    Schema untuk membuat ulasan baru.
    """
    destination_id: int = Field(..., description="ID destinasi yang akan diulas")
    rating: int = Field(..., ge=1, le=5, description="Rating antara 1 sampai 5")
    comment: Optional[str] = Field(None, description="Komentar tambahan dari pengguna")


class ReviewResponse(BaseModel):
    """
    Schema untuk menampilkan data ulasan dari database.
    """
    id: int
    destination_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True
