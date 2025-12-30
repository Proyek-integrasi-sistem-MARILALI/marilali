from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from src.accommodation.models import AccommodationSearch, AccommodationRecommendation
from src.accommodation.schemas import AccommodationSearchRequest
from src.itinerary.models import Itinerary
from datetime import datetime
import random


async def search_accommodations(user_id: int, data: AccommodationSearchRequest, db: AsyncSession):
    search_record = AccommodationSearch(
        user_id=user_id,
        location=data.location,
        check_in=data.check_in,
        check_out=data.check_out,
        guests=data.guests,
        max_price=data.max_price,
        min_rating=data.min_rating,
        amenities=data.amenities
    )
    db.add(search_record)
    
    # Calculate number of nights
    nights = (data.check_out - data.check_in).days
    
    # Generate AI recommendations
    recommendations = []
    sample_hotels = [
        {"name": "Sunset Beach Resort", "base_price": 150, "rating": 4.5},
        {"name": "Mountain View Hotel", "base_price": 120, "rating": 4.2},
        {"name": "City Center Inn", "base_price": 80, "rating": 3.8},
        {"name": "Luxury Palace Hotel", "base_price": 300, "rating": 4.8},
        {"name": "Budget Traveler Lodge", "base_price": 50, "rating": 3.5},
        {"name": "Eco Friendly Resort", "base_price": 180, "rating": 4.6},
    ]
    
    for hotel in sample_hotels:
        price_per_night = hotel["base_price"]
        total_price = price_per_night * nights
        
        # Apply budget filter
        budget_compatible = True
        if data.max_price and total_price > data.max_price:
            budget_compatible = False
            if not data.use_ai_recommendations:
                continue
        
        # Apply rating filter
        if data.min_rating and hotel["rating"] < data.min_rating:
            continue
        
        # Calculate AI recommendation score
        score = hotel["rating"] / 5.0
        if data.max_price:
            budget_efficiency = 1 - (total_price / data.max_price) if total_price <= data.max_price else 0.5
            score = (score + budget_efficiency) / 2
        
        recommendation_reason = f"Recommended based on {hotel['rating']}/5 rating"
        if budget_compatible:
            recommendation_reason += f" and fits within your budget of ${data.max_price or 'unlimited'}"
        
        recommendation = AccommodationRecommendation(
            user_id=user_id,
            hotel_name=hotel["name"],
            location=data.location,
            latitude=random.uniform(-90, 90),
            longitude=random.uniform(-180, 180),
            price_per_night=price_per_night,
            total_price=total_price,
            rating=hotel["rating"],
            amenities=data.amenities or ["WiFi", "AC", "Breakfast"],
            description=f"Beautiful {hotel['name']} in {data.location}",
            recommendation_score=round(score, 2),
            recommendation_reason=recommendation_reason,
            budget_compatible=budget_compatible,
            weather_compatible=True
        )
        db.add(recommendation)
        recommendations.append(recommendation)
    
    search_record.search_results_count = len(recommendations)
    await db.commit()
    
    return recommendations


async def get_search_history(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(AccommodationSearch)
        .where(AccommodationSearch.user_id == user_id)
        .order_by(AccommodationSearch.created_at.desc())
    )
    return result.scalars().all()


async def get_recommendations(user_id: int, itinerary_id: int = None, db: AsyncSession = None):
    query = select(AccommodationRecommendation).where(
        AccommodationRecommendation.user_id == user_id
    )
    
    if itinerary_id:
        query = query.where(AccommodationRecommendation.itinerary_id == itinerary_id)
    
    query = query.order_by(AccommodationRecommendation.recommendation_score.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def select_accommodation(user_id: int, accommodation_id: int, itinerary_id: int, db: AsyncSession):
    result = await db.execute(
        select(AccommodationRecommendation).where(
            AccommodationRecommendation.id == accommodation_id,
            AccommodationRecommendation.user_id == user_id
        )
    )
    accommodation = result.scalar_one_or_none()
    
    if not accommodation:
        raise HTTPException(status_code=404, detail="Accommodation not found")
    
    accommodation.itinerary_id = itinerary_id
    accommodation.is_selected = True
    await db.commit()
    await db.refresh(accommodation)
    
    return accommodation
