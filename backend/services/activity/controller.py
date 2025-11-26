from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
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
        cost=destination.price,
        day_number=data.day_number,
        start_time=data.start_time,
        end_time=data.end_time,
        sort_order=data.sort_order or 0,
        is_completed=False
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
    ).order_by(Activity.day_number, Activity.sort_order).all()


# ============================
# UPDATE ACTIVITY
# ============================
def update_activity(activity_id: int, user_id: int, data, db: Session):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Aktivitas tidak ditemukan")

    itinerary = db.query(Itinerary).filter(
        Itinerary.id == activity.itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=403, detail="Tidak punya akses")

    # Update only fields provided
    fields = ["title", "location", "note", "cost",
              "day_number", "start_time", "end_time",
              "sort_order", "is_completed"]

    for f in fields:
        val = getattr(data, f, None)
        if val is not None:
            setattr(activity, f, val)

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

    itinerary = db.query(Itinerary).filter(
        Itinerary.id == activity.itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=403, detail="Tidak punya akses")

    db.delete(activity)
    db.commit()
    return {"message": "Aktivitas berhasil dihapus"}


# ============================
# MARK COMPLETED
# ============================
def mark_completed(activity_id: int, user_id: int, db: Session):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Aktivitas tidak ditemukan")

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


# ============================
# DUPLICATE ACTIVITY
# ============================
def duplicate_activity(activity_id: int, user_id: int, db: Session):
    original = db.query(Activity).filter(Activity.id == activity_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Aktivitas tidak ditemukan")

    itinerary = db.query(Itinerary).filter(
        Itinerary.id == original.itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=403, detail="Tidak punya akses")

    # safer sort order
    max_sort = db.query(func.max(Activity.sort_order)).filter(
        Activity.itinerary_id == original.itinerary_id
    ).scalar() or 0

    new_activity = Activity(
        itinerary_id=original.itinerary_id,
        title=original.title + " (Copy)",
        location=original.location,
        note=original.note,
        cost=original.cost,
        day_number=original.day_number,
        start_time=original.start_time,
        end_time=original.end_time,
        sort_order=max_sort + 1,
        is_completed=False
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity
