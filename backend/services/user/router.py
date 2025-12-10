from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from services.user import controller
from services.user.schemas import (
    UserProfileResponse,
    UserUpdate,
    PasswordChange
)

from database.connection import get_db
from core.security import get_current_user
from database.models import User

router = APIRouter()


# ======================================
#            GET PROFILE
# ======================================
@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return controller.get_user_profile(current_user, db)


# ======================================
#           UPDATE PROFILE
# ======================================
@router.put("/me", response_model=UserProfileResponse)
def update_my_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return controller.update_user_profile(current_user, update_data, db)


# ======================================
#          CHANGE PASSWORD
# ======================================
@router.put("/me/password")
def change_my_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return controller.change_password(current_user, password_data, db)


# ======================================
#          DELETE ACCOUNT
# ======================================
@router.delete("/me")
def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return controller.delete_user_account(current_user, db)
