from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import Destination, Review

def get_all_destinations(db: Session):
    """
    Mengambil seluruh destinasi beserta rata-rata rating-nya.
    """
    destinations = db.query(Destination).all()
    results = []

    for d in destinations:
        avg_rating = (
            db.query(func.avg(Review.rating))
            .filter(Review.destination_id == d.id)
            .scalar()
        )

        results.append({
            "id": d.id,
            "name": d.name,
            "category": d.category,
            "location": d.location,
            "price": d.price,
            "description": d.description,
            "image_url": d.image_url,
            "average_rating": round(avg_rating, 2) if avg_rating else 0.0,
            "reviews": d.reviews or []
        })

    return results


def get_destination_by_id(destination_id: int, db: Session):
    """
    Mengambil detail satu destinasi berdasarkan ID.
    """
    destination = db.query(Destination).filter(Destination.id == destination_id).first()
    if not destination:
        return None

    avg_rating = (
        db.query(func.avg(Review.rating))
        .filter(Review.destination_id == destination.id)
        .scalar()
    )

    return {
        "id": destination.id,
        "name": destination.name,
        "category": destination.category,
        "location": destination.location,
        "price": destination.price,
        "description": destination.description,
        "image_url": destination.image_url,
        "average_rating": round(avg_rating, 2) if avg_rating else 0.0,
        "reviews": destination.reviews or []
    }
