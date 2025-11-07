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
