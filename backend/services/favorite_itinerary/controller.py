from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import FavoriteItinerary, Itinerary

def add_favorite_itinerary(user_id: int, itinerary_id: int, db: Session):
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")

    existing = db.query(FavoriteItinerary).filter(
        FavoriteItinerary.user_id == user_id,
        FavoriteItinerary.itinerary_id == itinerary_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Itinerary sudah difavoritkan")

    fav = FavoriteItinerary(user_id=user_id, itinerary_id=itinerary_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav


def remove_favorite_itinerary(user_id: int, itinerary_id: int, db: Session):
    fav = db.query(FavoriteItinerary).filter(
        FavoriteItinerary.user_id == user_id,
        FavoriteItinerary.itinerary_id == itinerary_id
    ).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorit itinerary tidak ditemukan")
    db.delete(fav)
    db.commit()
    return {"message": "Itinerary dihapus dari favorit"}


def list_favorite_itineraries(user_id: int, db: Session):
    return db.query(FavoriteItinerary).filter(FavoriteItinerary.user_id == user_id).all()
