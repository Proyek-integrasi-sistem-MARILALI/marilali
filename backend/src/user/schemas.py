from pydantic import EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
from src.schemas import CustomModel


class UserProfileResponse(CustomModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = None
    is_verified: int = 0
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserUpdate(CustomModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = None
    # Email should NOT be editable without verification
    # Use separate endpoint for email change


class PasswordChange(CustomModel):
    old_password: str
    new_password: str


class ForgotPasswordRequest(CustomModel):
    email: EmailStr


class ResetPasswordRequest(CustomModel):
    token: str
    new_password: str


class ProfilePictureUpdate(CustomModel):
    profile_picture: str  # Base64 encoded image or URL


class EmailChangeRequest(CustomModel):
    new_email: EmailStr
    password: str  # Require password confirmation
