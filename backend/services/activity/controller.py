from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import Destination, Activity, Itinerary


# ============================
# ADD DESTINATION → ACTIVITY
# ============================
def add_destination_to_itinerary(user_id: int, data, db: Session):
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == data.itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")

    destination = db.query(Destination).filter(
        Destination.id == data.destination_id
    ).first()

    if not destination:
        raise HTTPException(status_code=404, detail="Destinasi tidak ditemukan")

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


# ============================
# LIST ACTIVITIES
# ============================
def list_activities(itinerary_id: int, user_id: int, db: Session):
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")

    return db.query(Activity).filter(
        Activity.itinerary_id == itinerary_id
    ).all()


# ============================
# UPDATE ACTIVITY
# ============================
def update_activity(activity_id: int, user_id: int, data, db: Session):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Aktivitas tidak ditemukan")

    # Cek itinerary milik user
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == activity.itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=403, detail="Tidak punya akses")

    # Update field jika ada
    if data.title is not None:
        activity.title = data.title

    if data.location is not None:
        activity.location = data.location

    if data.note is not None:
        activity.note = data.note

    if data.cost is not None:
        activity.cost = data.cost

    db.commit()
    db.refresh(activity)
    return activity


# ============================
# DELETE ACTIVITY
# ============================
def delete_activity(activity_id: int, user_id: int, db: Session):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Aktivitas tidak ditemukan")

    # Validasi pemilik itinerary
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == activity.itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=403, detail="Tidak punya akses")

    db.delete(activity)
    db.commit()
    return {"message": "Aktivitas berhasil dihapus"}
