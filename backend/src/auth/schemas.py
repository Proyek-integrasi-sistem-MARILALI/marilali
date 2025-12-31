"""
Module: services.auth.schemas
Deskripsi:
Pydantic v2 schemas untuk validasi input/output pada fitur autentikasi.
"""

from pydantic import EmailStr, Field, ConfigDict
from datetime import datetime
from src.schemas import CustomModel


class UserCreate(CustomModel):
    """Schema untuk registrasi pengguna baru."""
    name: str = Field(..., min_length=1, max_length=100, examples=["John Doe"])
    email: EmailStr = Field(..., examples=["johndoe@example.com"])
    password: str = Field(..., min_length=6, max_length=100, examples=["securepassword"])


class UserLogin(CustomModel):
    """Schema untuk login pengguna."""
    email: EmailStr = Field(..., examples=["johndoe@example.com"])
    password: str = Field(..., examples=["securepassword"])


class UserResponse(CustomModel):
    """Schema untuk response data pengguna."""
    id: int
    name: str
    email: EmailStr
    created_at: datetime


class TokenResponse(CustomModel):
    """Schema untuk response token setelah login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(CustomModel):
    """Schema untuk request refresh token."""
    refresh_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])


class TokenRefreshResponse(CustomModel):
    """Schema untuk response setelah refresh token."""
    access_token: str
    token_type: str = "bearer"
