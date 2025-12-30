from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from src.transportation.models import FlightSearch, FlightRecommendation
from src.transportation.schemas import FlightSearchRequest
from datetime import timedelta
import random


async def search_flights(user_id: int, data: FlightSearchRequest, db: AsyncSession):
    # Save search history
    search_record = FlightSearch(
        user_id=user_id,
        origin=data.origin,
        destination=data.destination,
        departure_date=data.departure_date,
        return_date=data.return_date,
        passengers=data.passengers,
        cabin_class=data.cabin_class,
        max_price=data.max_price
    )
    db.add(search_record)
    
    # Generate AI-powered flight recommendations
    recommendations = []
    airlines = ["Garuda Indonesia", "Air Asia", "Lion Air", "Citilink", "Batik Air"]
    
    for i, airline in enumerate(airlines):
        # Generate flight details
        base_price = random.randint(800, 3000)
        duration = random.randint(60, 480)  # minutes
        stops = random.choice([0, 1, 2])
        
        # Adjust price based on cabin class
        class_multiplier = {"economy": 1.0, "business": 2.5, "first": 4.0}
        price = int(base_price * class_multiplier.get(data.cabin_class, 1.0))
        
        # Apply budget filter
        budget_compatible = True
        if data.max_price and price > data.max_price:
            budget_compatible = False
            if not data.use_ai_recommendations:
                continue
        
        # Calculate AI recommendation score
        score = 0.5
        if stops == 0:
            score += 0.3
        if budget_compatible:
            score += 0.2
        if data.max_price:
            budget_efficiency = 1 - (price / data.max_price) if price <= data.max_price else 0.3
            score = (score + budget_efficiency) / 2
        
        departure_time = data.departure_date + timedelta(hours=random.randint(6, 20))
        arrival_time = departure_time + timedelta(minutes=duration)
        
        recommendation_reason = f"{airline} - "
        if stops == 0:
            recommendation_reason += "Direct flight, "
        recommendation_reason += f"{duration // 60}h {duration % 60}m duration"
        if budget_compatible:
            recommendation_reason += f", fits within budget"
        
        recommendation = FlightRecommendation(
            user_id=user_id,
            airline=airline,
            flight_number=f"{airline[:2].upper()}{random.randint(100, 999)}",
            origin=data.origin,
            destination=data.destination,
            departure_time=departure_time,
            arrival_time=arrival_time,
            duration_minutes=duration,
            stops=stops,
            cabin_class=data.cabin_class,
            price=price,
            baggage_allowance="20kg checked + 7kg cabin",
            recommendation_score=round(score, 2),
            recommendation_reason=recommendation_reason,
            budget_compatible=budget_compatible,
            weather_optimized=True
        )
        db.add(recommendation)
        recommendations.append(recommendation)
    
    search_record.search_results_count = len(recommendations)
    await db.commit()
    
    return recommendations


async def get_search_history(user_id: int, db: AsyncSession):
    """Get flight search history."""
    result = await db.execute(
        select(FlightSearch)
        .where(FlightSearch.user_id == user_id)
        .order_by(FlightSearch.created_at.desc())
    )
    return result.scalars().all()


async def get_recommendations(user_id: int, itinerary_id: int = None, db: AsyncSession = None):
    """Get flight recommendations."""
    query = select(FlightRecommendation).where(
        FlightRecommendation.user_id == user_id
    )
    
    if itinerary_id:
        query = query.where(FlightRecommendation.itinerary_id == itinerary_id)
    
    query = query.order_by(FlightRecommendation.recommendation_score.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def select_flight(user_id: int, flight_id: int, itinerary_id: int, db: AsyncSession):
    """Select a flight for an itinerary."""
    result = await db.execute(
        select(FlightRecommendation).where(
            FlightRecommendation.id == flight_id,
            FlightRecommendation.user_id == user_id
        )
    )
    flight = result.scalar_one_or_none()
    
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    flight.itinerary_id = itinerary_id
    flight.is_selected = True
    await db.commit()
    await db.refresh(flight)
    
    return flight
