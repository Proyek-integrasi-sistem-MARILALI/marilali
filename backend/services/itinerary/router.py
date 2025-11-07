from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.itinerary import controller
from services.itinerary.schemas import ItineraryCreate, ItineraryResponse
from core.security import get_current_user
from database.connection import get_db
from database.models import User

router = APIRouter()

@router.post("/", response_model=ItineraryResponse)
def create_itinerary(
    data: ItineraryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.create_itinerary(current_user.id, data, db)


@router.get("/", response_model=list[ItineraryResponse])
def list_itineraries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.get_all_itineraries(current_user.id, db)


@router.get("/{itinerary_id}", response_model=ItineraryResponse)
def get_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.get_itinerary_by_id(itinerary_id, current_user.id, db)


@router.delete("/{itinerary_id}")
def delete_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.delete_itinerary(itinerary_id, current_user.id, db)
