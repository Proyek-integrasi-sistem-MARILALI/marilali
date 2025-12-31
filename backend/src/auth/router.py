"""
Module: services.auth.router
Deskripsi:
Async API endpoints untuk autentikasi - registrasi, login, logout, refresh token, dan profile.
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import service
from src.auth.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    TokenRefreshRequest,
    TokenRefreshResponse
)
from src.database import get_db
from src.auth.security import get_current_user, oauth2_scheme
from src.user.models import User


router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with name, email, and password."
)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Endpoint untuk registrasi pengguna baru."""
    return await service.register_user(user, db)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and return JWT access and refresh tokens."
)
async def login(
    user: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Endpoint untuk login pengguna."""
    return await service.login_user(user.email, user.password, db)


@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    summary="Refresh access token",
    description="Generate new access token using valid refresh token."
)
async def refresh_token(payload: TokenRefreshRequest):
    """Endpoint untuk refresh access token."""
    return await service.refresh_access_token(payload.refresh_token)


@router.post(
    "/logout",
    summary="User logout",
    description="Logout is handled client-side by removing tokens from storage."
)
async def logout(token: str = Depends(oauth2_scheme)):
    """
    Logout simbolik - token JWT stateless, jadi logout dilakukan di client.
    Client harus menghapus token dari storage (localStorage/sessionStorage).
    """
    return {
        "message": "Logout successful. Please remove tokens from client storage."
    }


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Retrieve logged-in user information based on JWT token."
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Endpoint untuk mendapatkan data user yang sedang login."""
    return current_user


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Send password reset link to user's email."
)
async def forgot_password(
    request: dict,  # {"email": "user@example.com"}
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint untuk request reset password.
    Mengirim link reset ke email pengguna.
    """
    from src.user.service import request_password_reset
    email = request.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    return await request_password_reset(email, db)


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset password with token",
    description="Reset password using token from email link."
)
async def reset_password(
    request: dict,  # {"token": "...", "new_password": "..."}
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint untuk reset password menggunakan token.
    Token didapat dari email reset password.
    """
    from src.user.service import reset_password_with_token
    token = request.get("token")
    new_password = request.get("new_password")
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token and new password are required")
    return await reset_password_with_token(token, new_password, db)


@router.post(
    "/verify-email",
    status_code=status.HTTP_200_OK,
    summary="Verify user email (MVP)",
    description="Mark user email as verified. In production, this would validate a token from email."
)
async def verify_user_email(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    MVP: Direct email verification for logged-in user.
    Production: Validate verification token from email link.
    """
    from src.user.service import verify_email
    return await verify_email(current_user.id, db)
