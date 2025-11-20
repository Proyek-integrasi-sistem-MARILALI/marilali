from services.recommendation.controller import get_recommendations
from services.weather.controller import get_weather_condition  # dibuat di langkah 5
from database.models import Destination
from sqlalchemy.orm import Session

def get_planner_recommendations(data, db: Session):
    # 1. Ambil rekomendasi dasar (kategori, area, budget)
    base_recommendations = get_recommendations(
        location=data.location,
        category=data.category,
        budget=data.budget,
        db=db
    )

    # 2. Dapatkan kondisi cuaca real-time / mock
    weather = get_weather_condition(data.location)

    results = []

    for item in base_recommendations:
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
            "rating": item["average_rating"],
            "weather_suitability": suitability,
        })

    return results
