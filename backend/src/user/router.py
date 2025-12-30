from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.user import service
from src.user.schemas import (
    UserProfileResponse, 
    UserUpdate, 
    PasswordChange,
    ProfilePictureUpdate,
    EmailChangeRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from src.database import get_db
from src.auth.security import get_current_user
from src.user.models import User


router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_user_profile(current_user, db)


@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.update_user_profile(current_user, update_data, db)


@router.put("/me/password")
async def change_my_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.change_password(current_user, password_data, db)


@router.put("/me/profile-picture", response_model=UserProfileResponse)
async def update_my_profile_picture(
    picture_data: ProfilePictureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.update_profile_picture(
        current_user, 
        picture_data.profile_picture, 
        db
    )


@router.put("/me/email")
async def change_my_email(
    email_data: EmailChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.change_email(
        current_user,
        email_data.new_email,
        email_data.password,
        db
    )


@router.delete("/me")
async def delete_my_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.delete_user_account(current_user, db)
