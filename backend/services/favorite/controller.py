from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import FavoriteDestination, Destination

def add_favorite(user_id: int, destination_id: int, db: Session):
    # cek apakah destinasi ada
    destination = db.query(Destination).filter(Destination.id == destination_id).first()
    if not destination:
        raise HTTPException(status_code=404, detail="Destinasi tidak ditemukan")

    # cek apakah sudah difavoritkan
    existing = db.query(FavoriteDestination).filter(
        FavoriteDestination.user_id == user_id,
        FavoriteDestination.destination_id == destination_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Destinasi sudah difavoritkan")

    fav = FavoriteDestination(user_id=user_id, destination_id=destination_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav


def remove_favorite(user_id: int, destination_id: int, db: Session):
    fav = db.query(FavoriteDestination).filter(
        FavoriteDestination.user_id == user_id,
        FavoriteDestination.destination_id == destination_id
    ).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorit tidak ditemukan")
    db.delete(fav)
    db.commit()
    return {"message": "Destinasi dihapus dari favorit"}


def list_favorites(user_id: int, db: Session):
    return db.query(FavoriteDestination).filter(FavoriteDestination.user_id == user_id).all()
