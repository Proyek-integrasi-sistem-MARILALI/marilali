from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.explorer import controller
from services.explorer.schemas import DestinationResponse
from database.connection import get_db

router = APIRouter()

@router.get("/", response_model=list[DestinationResponse])
def list_destinations(db: Session = Depends(get_db)):
    """
    Mendapatkan semua destinasi dengan rata-rata rating.
    """
    return controller.get_all_destinations(db)

@router.get("/{destination_id}", response_model=DestinationResponse)
def get_destination_detail(destination_id: int, db: Session = Depends(get_db)):
    """
    Mendapatkan detail satu destinasi beserta review-nya.
    """
    destination = controller.get_destination_by_id(destination_id, db)
    if not destination:
        raise HTTPException(status_code=404, detail="Destinasi tidak ditemukan")
    return destination

@router.get("/public-itineraries", response_model=list[ItineraryResponse])
def list_public_itineraries(db: Session = Depends(get_db)):
    return controller.get_public_itineraries(db)
