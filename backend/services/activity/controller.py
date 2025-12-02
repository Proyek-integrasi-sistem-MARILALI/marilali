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


def create_manual_activity(user_id: int, data, db: Session):
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == data.itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")

    activity = Activity(
        itinerary_id=data.itinerary_id,
        title=data.title,
        location=data.location,
        note=data.note,
        cost=data.cost,
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


def reorder_activities(user_id: int, items, db: Session):
    for item in items:
        activity = db.query(Activity).filter(Activity.id == item.activity_id).first()

        if not activity:
            continue  # skip jika tidak ditemukan

        # cek kepemilikan itinerary
        itinerary = db.query(Itinerary).filter(
            Itinerary.id == activity.itinerary_id,
            Itinerary.user_id == user_id
        ).first()

        if not itinerary:
            continue

        activity.sort_order = item.sort_order

    db.commit()
    return {"message": "Urutan aktivitas berhasil diperbarui"}


def mark_uncompleted(activity_id: int, user_id: int, db: Session):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Aktivitas tidak ditemukan")

    itinerary = db.query(Itinerary).filter(
        Itinerary.id == activity.itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=403, detail="Tidak punya akses")

    activity.is_completed = False
    db.commit()
    db.refresh(activity)
    return activity

def reset_day(itinerary_id: int, day_number: int, user_id: int, db: Session):
    # cek itinerary milik user
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=403, detail="Tidak punya akses ke itinerary")

    activities = db.query(Activity).filter(
        Activity.itinerary_id == itinerary_id,
        Activity.day_number == day_number
    ).all()

    if not activities:
        raise HTTPException(status_code=404, detail="Tidak ada aktivitas pada hari ini")

    for a in activities:
        a.is_completed = False

    db.commit()
    return {"message": "Semua aktivitas hari ini berhasil di-reset"}

def reset_itinerary(itinerary_id: int, user_id: int, db: Session):
    # cek itinerary milik user
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=403, detail="Tidak punya akses ke itinerary")

    activities = db.query(Activity).filter(
        Activity.itinerary_id == itinerary_id
    ).all()

    if not activities:
        return {"message": "Tidak ada aktivitas untuk di-reset"}

    for a in activities:
        a.is_completed = False

    db.commit()
    return {"message": "Semua aktivitas berhasil direset"}

def complete_all_activities(itinerary_id: int, user_id: int, db: Session):
    # Pastikan itinerary milik user
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=403, detail="Tidak punya akses ke itinerary")

    # Ambil semua aktivitas
    activities = db.query(Activity).filter(
        Activity.itinerary_id == itinerary_id
    ).all()

    if not activities:
        return {"message": "Tidak ada aktivitas untuk ditandai selesai"}

    # Tandai semuanya selesai
    for act in activities:
        act.is_completed = True

    db.commit()
    return {"message": "Semua aktivitas berhasil ditandai selesai"}

