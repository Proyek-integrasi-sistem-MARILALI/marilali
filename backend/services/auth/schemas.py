"""
Module: services.auth.schemas
Deskripsi:
Mendefinisikan model data Pydantic untuk validasi input dan output
pada fitur autentikasi (register, login, dan user response).
"""

from pydantic import BaseModel, EmailStr, Field


# =====================================================
#                  REGISTER USER
# =====================================================
class UserCreate(BaseModel):
    """
    Schema untuk input registrasi pengguna baru.
    """
    name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="johndoe@example.com")
    password: str = Field(
        ..., 
        min_length=6, 
        example="securepassword",
        description="Minimal 6 karakter"
    )


# =====================================================
#                     LOGIN USER
# =====================================================
class UserLogin(BaseModel):
    """
    Schema untuk input login pengguna.
    """
    email: EmailStr = Field(..., example="johndoe@example.com")
    password: str = Field(..., example="securepassword")


# =====================================================
#                    USER RESPONSE
# =====================================================
class UserResponse(BaseModel):
    """
    Schema untuk output data pengguna yang dikembalikan ke client.
    """
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True


# =====================================================
#               TOKEN RESPONSE (OPTIONAL)
# =====================================================
class TokenResponse(BaseModel):
    """
    Schema standar untuk token respons (opsional, tidak merusak kode kamu).
    Dipakai untuk login / refresh jika ingin lebih rapi.
    """
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
