from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import Destination, Review

def generate_recommendations(data, db: Session):

    # 1. Filter lokasi
    query = db.query(Destination).filter(
        Destination.location.ilike(f"%{data.location_area}%")
    )

    # 2. Filter kategori
    if data.preferred_categories:
        query = query.filter(Destination.category.in_(data.preferred_categories))

    destinations = query.all()

    result = []
    total_min_cost = 0

    for d in destinations:

        rating = (
            db.query(func.avg(Review.rating))
            .filter(Review.destination_id == d.id)
            .scalar()
        ) or 0

        ticket_price = d.price or 0

        # RULE: jangan kasih destinasi mahal kalau budget kecil
        if ticket_price > data.max_budget * 0.5:
            continue

        est_cost = ticket_price + 50000 + 5000  # bensin + parkir

        result.append({
            "id": d.id,
            "name": d.name,
            "category": d.category,
            "location": d.location,
            "price": ticket_price,
            "image_url": d.image_url,
            "rating": round(rating, 1),
            "estimated_cost": est_cost
        })

        total_min_cost += est_cost

    # Sort by cheapest
    result = sorted(result, key=lambda x: x["estimated_cost"])

    return {
        "total_min_cost": total_min_cost,
        "destinations": result
    }
