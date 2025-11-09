from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.user_preferences import controller
from services.user_preferences.schemas import PreferenceBase, PreferenceResponse
from core.security import get_current_user
from database.connection import get_db
from database.models import User

router = APIRouter()

@router.get("/", response_model=PreferenceResponse)
def get_my_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.get_preferences(current_user.id, db)

@router.put("/", response_model=PreferenceResponse)
def update_my_preferences(
    data: PreferenceBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.update_preferences(current_user.id, data, db)
