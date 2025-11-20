from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import Destination, Activity, Itinerary

def add_destination_to_itinerary(user_id: int, data, db: Session):
    # cek itinerary ada dan milik user
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == data.itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")

    # cek destinasi ada
    destination = db.query(Destination).filter(
        Destination.id == data.destination_id
    ).first()

    if not destination:
        raise HTTPException(status_code=404, detail="Destinasi tidak ditemukan")

    # buat activity baru
    activity = Activity(
        itinerary_id=data.itinerary_id,
        title=destination.name,
        location=destination.location,
        note=destination.description,
        cost=destination.price
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def list_activities(itinerary_id: int, user_id: int, db: Session):
    return db.query(Activity).filter(
        Activity.itinerary_id == itinerary_id
    ).all()
