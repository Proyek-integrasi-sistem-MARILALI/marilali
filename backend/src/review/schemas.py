"""
Module: services.review.schemas
Deskripsi:
Pydantic v2 schemas untuk validasi input/output data review destinasi wisata.
"""

from pydantic import Field, ConfigDict
from typing import Optional
from datetime import datetime
from src.schemas import CustomModel


class ReviewCreate(CustomModel):
    """Schema untuk membuat ulasan baru."""
    destination_id: int = Field(..., description="ID destinasi yang akan diulas")
    rating: int = Field(..., ge=1, le=5, description="Rating antara 1 sampai 5")
    comment: Optional[str] = Field(None, description="Komentar tambahan dari pengguna")


class ReviewResponse(CustomModel):
    """Schema untuk menampilkan data ulasan dari database."""
    id: int
    destination_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    user_id: int
