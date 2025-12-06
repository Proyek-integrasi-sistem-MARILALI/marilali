from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import Itinerary, Flight, Accommodation, Activity
from sqlalchemy import func


def get_itinerary_summary(itinerary_id: int, user_id: int, db: Session):
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")

    # Total biaya flight
    total_flight = db.query(func.sum(Flight.price)).filter(
        Flight.itinerary_id == itinerary_id
    ).scalar() or 0

    # Total biaya hotel
    total_accommodation = 0
    accommodations = db.query(Accommodation).filter(
        Accommodation.itinerary_id == itinerary_id
    ).all()

    for a in accommodations:
        if a.check_in and a.check_out:
            nights = max(0, (a.check_out - a.check_in).days)
            total_accommodation += (a.price_per_night or 0) * nights

    # Total biaya aktivitas
    total_activity = db.query(func.sum(Activity.cost)).filter(
        Activity.itinerary_id == itinerary_id
    ).scalar() or 0

    total_all = total_flight + total_accommodation + total_activity

    return {
        "itinerary_id": itinerary_id,
        "title": itinerary.title,
        "total_flight": total_flight,
        "total_accommodation": total_accommodation,
        "total_activity": total_activity,
        "grand_total": total_all
    }
