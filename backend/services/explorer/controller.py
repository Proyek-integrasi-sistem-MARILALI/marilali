from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import Destination, Review, Itinerary, FavoriteItinerary


# ============================================
# DESTINASI
# ============================================
def get_all_destinations(db: Session):
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


# ============================================
# PUBLIC ITINERARIES
# ============================================
def get_public_itineraries(db: Session, page: int, limit: int, sort: str, search: str):
    query = db.query(Itinerary).filter(Itinerary.is_public == True)

    # 🔍 Search by title
    if search:
        query = query.filter(Itinerary.title.ilike(f"%{search}%"))

    # 🔽 Sorting
    if sort == "newest":
        query = query.order_by(Itinerary.created_at.desc())

    elif sort == "favorites":
        query = (
            query.outerjoin(FavoriteItinerary)
            .group_by(Itinerary.id)
            .order_by(func.count(FavoriteItinerary.id).desc())
        )

    elif sort == "duration":
        query = query.order_by((Itinerary.end_date - Itinerary.start_date).asc())

    # 📄 Pagination
    total = query.count()
    itineraries = query.offset((page - 1) * limit).limit(limit).all()

    # ✨ Format supaya sesuai schema PublicItineraryListResponse
    formatted = []
    for it in itineraries:
        formatted.append({
            "id": it.id,
            "title": it.title,
            "start_date": it.start_date,
            "end_date": it.end_date,
            "budget": it.budget,
            "created_at": it.created_at,
        })

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": formatted
    }


def get_single_public_itinerary(itinerary_id: int, db: Session):
    it = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.is_public == True
    ).first()

    if not it:
        return None

    # cocok dgn PublicItineraryResponse schema
    return {
        "id": it.id,
        "title": it.title,
        "description": getattr(it, "description", None),
        "start_date": it.start_date,
        "end_date": it.end_date,
        "budget": it.budget,
        "is_public": it.is_public,
        "created_at": it.created_at,
    }
