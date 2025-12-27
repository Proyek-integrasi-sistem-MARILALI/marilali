from services.recommendation.controller import generate_recommendations
from services.weather.controller import get_weather_condition
from sqlalchemy.orm import Session


def get_planner_recommendations(data, db: Session):
    # 1. Ambil rekomendasi dasar
    base = generate_recommendations(data, db)

    destinations = base["destinations"]

    # 2. Ambil kondisi cuaca
    weather = get_weather_condition(data.location_area)

    results = []

    for item in destinations:
        suitability = "good"

        if weather == "rainy" and item["category"] in ["Outdoor", "Beach"]:
            suitability = "bad"
        elif weather == "cloudy" and item["category"] == "Beach":
            suitability = "medium"

        results.append({
            "destination_id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "location": item["location"],
            "price": item["price"],
            "rating": item["rating"],
            "estimated_cost": item["estimated_cost"],
            "weather_suitability": suitability,
        })

    return {
        "weather": weather,
        "total_min_cost": base["total_min_cost"],
        "recommendations": results
    }
