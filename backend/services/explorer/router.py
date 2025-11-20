from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from services.explorer import controller
from services.explorer.schemas import (
    DestinationResponse,
    PublicItineraryResponse,
    PublicItineraryListResponse
)
from database.connection import get_db

router = APIRouter()


# ==========================
#   DESTINATIONS
# ==========================

@router.get("/", response_model=list[DestinationResponse])
def list_destinations(db: Session = Depends(get_db)):
    return controller.get_all_destinations(db)


@router.get("/destination/{destination_id}", response_model=DestinationResponse)
def get_destination_detail(destination_id: int, db: Session = Depends(get_db)):
    destination = controller.get_destination_by_id(destination_id, db)
    if not destination:
        raise HTTPException(status_code=404, detail="Destinasi tidak ditemukan")
    return destination


# ==========================
#   PUBLIC ITINERARIES
# ==========================

@router.get("/public-itineraries", response_model=PublicItineraryListResponse)
def list_public_itineraries(
    page: int = 1,
    limit: int = 10,
    sort: str = "newest",     # newest | favorites | duration
    search: str = "",
    db: Session = Depends(get_db)
):
    """
    Mengambil semua itinerary publik dengan pagination & sorting.
    """
    return controller.get_public_itineraries(db, page, limit, sort, search)


@router.get("/public-itineraries/{itinerary_id}", response_model=PublicItineraryResponse)
def get_public_itinerary_detail(itinerary_id: int, db: Session = Depends(get_db)):
    """
    Mengambil detail satu itinerary publik.
    """
    itinerary = controller.get_single_public_itinerary(itinerary_id, db)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan atau tidak publik")
    return itinerary
