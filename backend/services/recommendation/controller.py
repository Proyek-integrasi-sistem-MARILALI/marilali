from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import Destination, Review

def recommend_destinations_by_budget(db: Session, budget: int, sort: str = "cheapest"):
    """
    Mengembalikan destinasi yang sesuai budget user,
    bisa dipakai oleh Explorer & Planner.
    """

    query = db.query(Destination).filter(Destination.price <= budget)

    # Sorting opsional
    if sort == "cheapest":
        query = query.order_by(Destination.price.asc())
    elif sort == "rating":
        query = query.outerjoin(Review).group_by(Destination.id).order_by(
            func.avg(Review.rating).desc()
        )
    elif sort == "popular":
        query = query.outerjoin(Review).group_by(Destination.id).order_by(
            func.count(Review.id).desc()
        )

    destinations = query.all()

    results = []
    for d in destinations:
        avg_rating = db.query(func.avg(Review.rating)) \
            .filter(Review.destination_id == d.id).scalar()

        results.append({
            "id": d.id,
            "name": d.name,
            "category": d.category,
            "location": d.location,
            "price": d.price,
            "description": d.description,
            "image_url": d.image_url,
            "average_rating": round(avg_rating, 2) if avg_rating else 0.0,
        })

    return results
