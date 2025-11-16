from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import FavoriteDestination, FavoriteItinerary


# =====================
# FAVORITE DESTINATION
# =====================
def add_favorite_destination(user_id: int, data, db: Session):
    exists = db.query(FavoriteDestination).filter_by(
        user_id=user_id, destination_id=data.destination_id
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="Destinasi sudah difavoritkan")

    fav = FavoriteDestination(
        user_id=user_id,
        destination_id=data.destination_id
    )
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav


def remove_favorite_destination(user_id: int, destination_id: int, db: Session):
    fav = db.query(FavoriteDestination).filter_by(
        user_id=user_id, destination_id=destination_id
    ).first()

    if not fav:
        raise HTTPException(status_code=404, detail="Destinasi tidak ada di favorit")

    db.delete(fav)
    db.commit()
    return {"message": "Destinasi dihapus dari favorit"}


def list_favorite_destinations(user_id: int, db: Session):
    return db.query(FavoriteDestination).filter_by(user_id=user_id).all()



# =====================
# FAVORITE ITINERARY
# =====================
def add_favorite_itinerary(user_id: int, data, db: Session):
    exists = db.query(FavoriteItinerary).filter_by(
        user_id=user_id, itinerary_id=data.itinerary_id
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="Itinerary sudah difavoritkan")

    fav = FavoriteItinerary(
        user_id=user_id,
        itinerary_id=data.itinerary_id
    )
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav


def remove_favorite_itinerary(user_id: int, itinerary_id: int, db: Session):
    fav = db.query(FavoriteItinerary).filter_by(
        user_id=user_id, itinerary_id=itinerary_id
    ).first()

    if not fav:
        raise HTTPException(status_code=404, detail="Itinerary tidak ada di favorit")

    db.delete(fav)
    db.commit()
    return {"message": "Itinerary dihapus dari favorit"}


def list_favorite_itineraries(user_id: int, db: Session):
    return db.query(FavoriteItinerary).filter_by(user_id=user_id).all()
