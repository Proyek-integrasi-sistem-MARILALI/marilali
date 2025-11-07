"""
Module: services.auth.schemas
Deskripsi:
Mendefinisikan model data (schema) menggunakan Pydantic untuk validasi input
dan output pada fitur autentikasi (register, login, dan user response).
"""

from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    """
    Schema untuk input registrasi pengguna baru.
    """
    name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="johndoe@example.com")
    password: str = Field(..., min_length=6, example="securepassword")

class UserLogin(BaseModel):
    """
    Schema untuk input login pengguna.
    """
    email: EmailStr = Field(..., example="johndoe@example.com")
    password: str = Field(..., example="securepassword")

class UserResponse(BaseModel):
    """
    Schema untuk output data pengguna yang dikembalikan ke client.
    """
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True
