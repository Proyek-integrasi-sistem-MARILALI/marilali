from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import Itinerary, Flight, Accommodation

def create_itinerary(user_id: int, data, db: Session):
    new_itinerary = Itinerary(
        user_id=user_id,
        title=data.title,
        start_date=data.start_date,
        end_date=data.end_date,
        budget=data.budget
    )
    db.add(new_itinerary)
    db.commit()
    db.refresh(new_itinerary)
    return new_itinerary


def get_all_itineraries(user_id: int, db: Session):
    return db.query(Itinerary).filter(Itinerary.user_id == user_id).all()


def get_itinerary_by_id(itinerary_id: int, user_id: int, db: Session):
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")
    return itinerary


def delete_itinerary(itinerary_id: int, user_id: int, db: Session):
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")

    db.delete(itinerary)
    db.commit()
    return {"message": "Itinerary berhasil dihapus"}


def get_completed_itineraries(user_id: int, db: Session):
    """
    Mengambil semua itinerary yang statusnya 'completed'.
    """
    return db.query(Itinerary).filter(
        Itinerary.user_id == user_id,
        Itinerary.status == "completed"
    ).all()


def mark_itinerary_complete(itinerary_id: int, user_id: int, db: Session):
    """
    Menandai itinerary sebagai selesai.
    """
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")

    itinerary.status = "completed"
    db.commit()
    db.refresh(itinerary)

    return {"message": "Itinerary ditandai selesai", "status": itinerary.status}

def copy_itinerary(itinerary_id: int, user_id: int, db: Session):
    """
    Menyalin itinerary beserta flights & accommodations.
    """
    # Cek itinerary asli
    original = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not original:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")

    # Buat itinerary baru
    new_itinerary = Itinerary(
        user_id=user_id,
        title=original.title + " (Copy)",
        start_date=original.start_date,
        end_date=original.end_date,
        budget=original.budget,
        status="planned",
    )
    db.add(new_itinerary)
    db.commit()
    db.refresh(new_itinerary)

    # Copy Flights
    original_flights = db.query(Flight).filter(Flight.itinerary_id == itinerary_id).all()
    for f in original_flights:
        new_flight = Flight(
            itinerary_id=new_itinerary.id,
            airline=f.airline,
            departure_city=f.departure_city,
            arrival_city=f.arrival_city,
            departure_time=f.departure_time,
            arrival_time=f.arrival_time,
            price=f.price,
        )
        db.add(new_flight)

    # Copy Accommodations
    original_accommodations = db.query(Accommodation).filter(Accommodation.itinerary_id == itinerary_id).all()
    for a in original_accommodations:
        new_accommodation = Accommodation(
            itinerary_id=new_itinerary.id,
            name=a.name,
            location=a.location,
            check_in=a.check_in,
            check_out=a.check_out,
            price_per_night=a.price_per_night,
        )
        db.add(new_accommodation)

    db.commit()
    db.refresh(new_itinerary)
    return new_itinerary


def share_itinerary(itinerary_id: int, user_id: int, db: Session):
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == user_id
    ).first()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")

    itinerary.is_public = True
    db.commit()
    db.refresh(itinerary)

    return itinerary


def get_public_itineraries(db: Session):
    return db.query(Itinerary).filter(Itinerary.is_public == True).all()
