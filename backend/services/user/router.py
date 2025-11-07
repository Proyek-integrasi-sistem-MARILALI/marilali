from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.user import controller
from services.user.schemas import UserProfileResponse, UserUpdate
from database.connection import get_db
from core.security import get_current_user
from database.models import User
from services.user.schemas import PasswordChange

router = APIRouter()

@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.get_user_profile(current_user, db)


@router.put("/me", response_model=UserProfileResponse)
def update_my_profile(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update profil pengguna (nama/email).
    """
    return controller.update_user_profile(current_user, update_data, db)


@router.put("/me/password")
def change_my_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ganti password pengguna.
    """
    return controller.change_password(current_user, password_data, db)


@router.delete("/me")
def delete_my_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Hapus akun pengguna.
    """
    return controller.delete_user_account(current_user, db)

# Endpoint tambahan untuk fitur user dapat ditambahkan di sini