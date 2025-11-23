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
        
    if data.day_number is not None:
        activity.day_number = data.day_number

    if data.start_time is not None:
        activity.start_time = data.start_time

    if data.end_time is not None:
        activity.end_time = data.end_time

    if data.sort_order is not None:
        activity.sort_order = data.sort_order

    if data.is_completed is not None:
        activity.is_completed = data.is_completed


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


def mark_completed(activity_id: int, user_id: int, db: Session):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Aktivitas tidak ditemukan")

    # validasi kepemilikan
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == activity.itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=403, detail="Tidak punya akses")

    activity.is_completed = True
    db.commit()
    db.refresh(activity)
    return activity


def duplicate_activity(activity_id: int, user_id: int, db: Session):
    original = db.query(Activity).filter(Activity.id == activity_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Aktivitas tidak ditemukan")

    # validasi pemilik itinerary
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == original.itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=403, detail="Tidak punya akses")

    new_activity = Activity(
        itinerary_id=original.itinerary_id,
        title=original.title + " (Copy)",
        location=original.location,
        note=original.note,
        cost=original.cost,
        day_number=original.day_number,
        start_time=original.start_time,
        end_time=original.end_time,
        sort_order=original.sort_order + 1,  
        is_completed=False
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity

