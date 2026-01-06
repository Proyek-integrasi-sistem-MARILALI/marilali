from pydantic import EmailStr, Field, ConfigDict
from datetime import datetime
from src.schemas import CustomModel


class UserCreate(CustomModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["John Doe"])
    email: EmailStr = Field(..., examples=["johndoe@example.com"])
    password: str = Field(..., min_length=6, max_length=100, examples=["securepassword"])


class UserLogin(CustomModel):
    email_or_username: str = Field(..., examples=["johndoe@example.com", "John Doe"], description="Email address or username")
    password: str = Field(..., examples=["securepassword"])


class UserResponse(CustomModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime


class TokenResponse(CustomModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(CustomModel):
    refresh_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])


class TokenRefreshResponse(CustomModel):
    access_token: str
    token_type: str = "bearer"
