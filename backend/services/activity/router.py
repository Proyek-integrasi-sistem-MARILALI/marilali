from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.activity import controller
from services.activity.schemas import ActivityCreate, ActivityResponse
from core.security import get_current_user
from database.connection import get_db
from database.models import User

router = APIRouter()

@router.post("/", response_model=ActivityResponse)
def add_to_itinerary(
    data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.add_destination_to_itinerary(current_user.id, data, db)


@router.get("/{itinerary_id}", response_model=list[ActivityResponse])
def get_activities(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.list_activities(itinerary_id, current_user.id, db)

