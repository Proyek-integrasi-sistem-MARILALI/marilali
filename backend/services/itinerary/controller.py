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
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id, Itinerary.user_id == user_id).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")
    return itinerary


def delete_itinerary(itinerary_id: int, user_id: int, db: Session):
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id, Itinerary.user_id == user_id).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")
    db.delete(itinerary)
    db.commit()
    return {"message": "Itinerary berhasil dihapus"}


def get_completed_itineraries(user_id: int, db: Session):
    """
    Mengambil semua itinerary dengan status 'completed' milik user.
    """
    return db.query(Itinerary).filter(
        Itinerary.user_id == user_id,
        Itinerary.status == "completed"
    ).all()


def mark_itinerary_as_completed(itinerary_id: int, user_id: int, db: Session):
    """
    Mengubah status itinerary menjadi 'completed'.
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
    return itinerary


# def get_itinerary_details(itinerary_id: int, user_id: int, db: Session):
#     """
#     Mengambil detail itinerary beserta penerbangan dan akomodasi terkait.
#     """
#     itinerary = db.query(Itinerary).filter(
#         Itinerary.id == itinerary_id,
#         Itinerary.user_id == user_id
#     ).first()
#     if not itinerary:
#         raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")

#     flights = db.query(Flight).filter(Flight.itinerary_id == itinerary_id).all()
#     accommodations = db.query(Accommodation).filter(Accommodation.itinerary_id == itinerary_id).all()

#     return {
#         "itinerary": itinerary,
#         "flights": flights,
#         "accommodations": accommodations
#     }

