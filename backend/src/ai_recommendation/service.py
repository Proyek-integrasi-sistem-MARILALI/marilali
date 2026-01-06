from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from fastapi import HTTPException
import asyncio

from src.ai_recommendation.models import AIRecommendation, RecommendationSession
# from src.user.feedback_models import AIFeedback  # Module not found
from src.destination.models import Destination
from src.weather.weather_models import Weather
from src.review.models import Review
# from src.user_preferences.models import UserPreference  # Module not found
from src.user.models import User
from src.ai_recommendation.agents import get_travel_recommendations
from utils.weather_analyzer import analyze_weather_for_travel
from utils.budget_optimizer import (
    optimize_budget_allocation,
    find_budget_friendly_alternatives,
    check_budget_status
)
from utils.amadeus_client import get_amadeus_client


async def create_recommendation_session(
    user_id: int,
    session_type: str,
    context: Dict,
    db: AsyncSession
) -> RecommendationSession:
    """
    Create a new recommendation session.
    
    Args:
        user_id: ID of user
        session_type: Type (destination, itinerary, activity)
        context: Context data (budget, dates, preferences)
        db: Database session
        
    Returns:
        Created session
    """
    session = RecommendationSession(
        user_id=user_id,
        session_type=session_type,
        filters=context,
        created_at=datetime.utcnow()
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session


async def get_destination_recommendations(
    user_id: int,
    db: AsyncSession,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    travel_dates: Optional[Dict] = None,
    preferences: Optional[List[str]] = None,
    limit: int = 10
) -> List[AIRecommendation]:
    """
    Get AI-powered destination recommendations using Langbase RAG + local database.
    
    Flow:
    1. Query Langbase memory with user preferences to find relevant destinations
    2. Enrich with local database data (ratings, reviews, weather)
    3. Apply budget optimization and weather scoring
    4. Return personalized recommendations
    
    Args:
        user_id: ID of user
        budget_min: Minimum budget in IDR
        budget_max: Maximum budget in IDR
        travel_dates: Dict with start_date and end_date (ISO format)
        preferences: List of preferred categories (temple, beach, etc.)
        limit: Max number of recommendations
        db: Database session
        
    Returns:
        List of AI recommendations with confidence scores
    """
    # Build query string for Langbase based on preferences
    if preferences and len(preferences) > 0:
        user_query = f"Find destinations with these preferences: {', '.join(preferences)}"
    else:
        user_query = "Find popular destinations in Bali"
    
    if budget_max:
        user_query += f" with budget up to Rp {budget_max:,.0f}"
    
    # Get recommendations from Langbase RAG + database
    langbase_result = await get_travel_recommendations(
        user_query=user_query,
        db=db,
        travel_dates=travel_dates,
        budget_max=budget_max,
        top_k=limit
    )
    
    if not langbase_result or not langbase_result.get("destinations"):
        # Fallback to local database if Langbase fails
        print("[WARNING] Langbase returned no results, falling back to local database")
        return await _get_local_recommendations(
            user_id=user_id,
            db=db,
            budget_min=budget_min,
            budget_max=budget_max,
            travel_dates=travel_dates,
            preferences=preferences,
            limit=limit
        )
    
    # Create recommendation session
    context = {
        "budget_min": budget_min,
        "budget_max": budget_max,
        "travel_dates": travel_dates,
        "preferences": preferences,
        "query": user_query
    }
    
    session = await create_recommendation_session(
        user_id=user_id,
        session_type="destination",
        context=context,
        db=db
    )
    
    # Convert Langbase results to AIRecommendation objects
    recommendations = []
    for rec_data in langbase_result.get("recommendations", [])[:limit]:
        destination = rec_data.get("destination")
        if not destination:
            continue
        
        # Re-fetch destination from current session to ensure it exists and is attached
        result = await db.execute(
            select(Destination).where(Destination.id == destination.id)
        )
        destination_in_session = result.scalar_one_or_none()
        
        if not destination_in_session:
            print(f"[WARNING] Destination ID {destination.id} not found in database, skipping")
            continue
            
        # Calculate dynamic confidence score based on multiple factors
        confidence_score = _calculate_confidence_score(
            destination=destination_in_session,
            weather_data=rec_data.get("weather", {}),
            budget_match=rec_data.get("budget_match", True),
            rating=destination_in_session.rating
        )
        
        recommendation = AIRecommendation(
            session_id=session.id,
            user_id=user_id,
            destination_id=destination_in_session.id,
            recommendation_type="destination",
            confidence_score=confidence_score,
            reasoning=rec_data.get("reasoning", {}),
            created_at=datetime.utcnow()
        )
        
        db.add(recommendation)
        recommendations.append(recommendation)
    
    await db.commit()
    
    # Refresh to get relationships - eagerly load destination with reviews
    for rec in recommendations:
        await db.refresh(rec)
        # Eagerly load destination and its reviews to avoid lazy loading issues
        if rec.destination:
            await db.refresh(rec.destination, ["reviews"])
    
    # Task 2.1: Enrich with live flight prices (top 3 only, non-blocking)
    if travel_dates and len(recommendations) > 0:
        asyncio.create_task(_enrich_with_flight_prices(recommendations[:3], travel_dates, db))
    
    return recommendations


async def _get_local_recommendations(
    user_id: int,
    db: AsyncSession,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    travel_dates: Optional[Dict] = None,
    preferences: Optional[List[str]] = None,
    limit: int = 10
) -> List[AIRecommendation]:
    """
    Fallback: Get recommendations from local database only (original implementation).
    Used when Langbase is unavailable or returns no results.
    """
    # Get user preferences
    # user_prefs_result = await db.execute(
    #     select(UserPreference).where(UserPreference.user_id == user_id)
    # )
    # user_prefs = user_prefs_result.scalar_one_or_none()
    user_prefs = None  # Placeholder until UserPreference model is created
    
    # Build query for destinations
    query = select(Destination).options(selectinload(Destination.reviews))
    
    filters = []
    
    # Budget filter
    if budget_min is not None or budget_max is not None:
        if budget_min:
            filters.append(Destination.price >= budget_min)
        if budget_max:
            filters.append(Destination.price <= budget_max)
    
    # Category/preference filter - also search by name/location if preferences provided
    if preferences and len(preferences) > 0:
        # Try both category match AND name/location search for flexibility
        pref_filter = or_(
            Destination.category.in_(preferences),
            *[Destination.name.ilike(f"%{pref}%") for pref in preferences],
            *[Destination.location.ilike(f"%{pref}%") for pref in preferences]
        )
        filters.append(pref_filter)
    elif user_prefs and user_prefs.preferred_categories:
        filters.append(Destination.category.in_(user_prefs.preferred_categories))
    
    # Apply filters
    if filters:
        query = query.where(and_(*filters))
    
    # Order by rating
    query = query.order_by(
        Destination.rating.desc().nullslast(),
        Destination.id.desc()
    ).limit(limit * 2)  # Get more to score
    
    result = await db.execute(query)
    destinations = result.scalars().all()
    
    print(f"[DB FALLBACK] Found {len(destinations)} destinations matching filters")
    if destinations:
        print(f"[DB FALLBACK] Sample destinations: {[f'{d.id}:{d.name}' for d in destinations[:3]]}")
    
    # Create recommendation session
    context = {
        "budget_min": budget_min,
        "budget_max": budget_max,
        "travel_dates": travel_dates,
        "preferences": preferences or (user_prefs.preferred_categories if user_prefs else [])
    }
    
    session = await create_recommendation_session(
        user_id=user_id,
        session_type="destination",
        context=context,
        db=db
    )
    
    # Score and create recommendations
    recommendations = []
    
    # Find budget-friendly alternatives if budget_max specified
    filtered_destinations = destinations[:limit]
    if budget_max:
        # Convert destinations to dict format for budget optimizer
        dest_dicts = [
            {"id": d.id, "name": d.name, "price": float(d.price), "destination": d}
            for d in destinations
        ]
        affordable = find_budget_friendly_alternatives(
            items=dest_dicts,
            max_price=int(budget_max)
        )
        # Get back destination objects
        filtered_destinations = [d["destination"] for d in affordable[:limit]]
    
    for dest in filtered_destinations:
        # Calculate confidence score based on multiple factors
        confidence_score = await _calculate_destination_score(
            destination=dest,
            budget_max=budget_max,
            user_prefs=user_prefs,
            travel_dates=travel_dates,
            db=db
        )
        
        # Generate reasoning
        reasoning_text = _generate_recommendation_reasoning(
            destination=dest,
            confidence_score=confidence_score,
            budget_match=(budget_min <= dest.price <= budget_max) if budget_min and budget_max else True
        )
        
        # Create recommendation with all context in reasoning field
        recommendation = AIRecommendation(
            session_id=session.id,
            user_id=user_id,
            destination_id=dest.id,
            recommendation_type="destination",
            confidence_score=confidence_score,
            reasoning={
                "text": reasoning_text,
                "budget_context": {
                    "destination_price": float(dest.price),
                    "user_budget_min": budget_min,
                    "user_budget_max": budget_max,
                    "budget_fit": "within" if (budget_min and budget_max and budget_min <= dest.price <= budget_max) else "near"
                },
                "weather_context": travel_dates
            },
            created_at=datetime.utcnow()
        )
        
        db.add(recommendation)
        recommendations.append(recommendation)
    
    await db.commit()
    
    # Refresh to get relationships and validate destinations exist
    valid_recommendations = []
    for rec in recommendations:
        await db.refresh(rec, ["destination"])
        if rec.destination:
            # Eagerly load reviews
            await db.refresh(rec.destination, ["reviews"])
            valid_recommendations.append(rec)
        else:
            print(f"[WARNING] Recommendation {rec.id} points to non-existent destination_id {rec.destination_id}")
            db.delete(rec)
    
    # Use only valid recommendations
    recommendations = valid_recommendations
    
    if len(recommendations) < len(destinations):
        await db.commit()  # Commit deletions
    
    # Add budget optimization if budget_max provided
    if budget_max and travel_dates:
        # Calculate trip duration
        start = travel_dates.get("start_date")
        end = travel_dates.get("end_date")
        
        if start and end:
            if isinstance(start, str):
                start = datetime.fromisoformat(start)
            if isinstance(end, str):
                end = datetime.fromisoformat(end)
            
            trip_days = (end - start).days if hasattr(end - start, 'days') else 7
            
            # Get optimized budget allocation
            budget_breakdown = optimize_budget_allocation(
                total_budget=int(budget_max),
                trip_days=trip_days
            )
            
            # Add budget optimization to each recommendation's reasoning
            for rec in recommendations:
                if not rec.reasoning:
                    rec.reasoning = {}
                if "budget_context" not in rec.reasoning:
                    rec.reasoning["budget_context"] = {}
                    
                rec.reasoning["budget_context"]["optimized_allocation"] = budget_breakdown
                rec.reasoning["budget_context"]["trip_days"] = trip_days
                
                # Check if destination fits within recommended allocation
                dest_price = rec.reasoning["budget_context"].get("destination_price", 0)
                daily_budget = budget_breakdown.get("daily_budget", 0)
                
                rec.reasoning["budget_context"]["budget_status"] = check_budget_status(
                    spent=int(dest_price),
                    budget=int(budget_max)
                )
    
    # Task 2.1: Enrich with live flight prices (top 3 only, non-blocking)
    if travel_dates and len(recommendations) > 0:
        asyncio.create_task(_enrich_with_flight_prices(recommendations[:3], travel_dates, db))
    
    print(f"[DB FALLBACK] Returning {len(recommendations)} recommendations to frontend")
    for rec in recommendations[:3]:
        dest = rec.destination if hasattr(rec, 'destination') and rec.destination else None
        if dest:
            print(f"  - ID:{rec.id}, Dest:{dest.id}:{dest.name}, Score:{rec.confidence_score:.2f}")
        else:
            print(f"  - ID:{rec.id}, Dest:MISSING, Score:{rec.confidence_score:.2f}")
    
    return recommendations


async def _calculate_destination_score(
    destination: Destination,
    budget_max: Optional[float],
    user_prefs: Optional[Any],  # UserPreference model not yet created
    travel_dates: Optional[Dict] = None,
    db: AsyncSession = None
) -> float:
    """
    Calculate confidence score for destination recommendation.
    Score: 0.0 - 1.0 based on multiple factors including weather.
    """
    score = 0.0
    
    # Factor 1: Rating (30% weight - reduced to make room for weather)
    if destination.rating:
        score += (destination.rating / 5.0) * 0.3
    
    # Factor 2: Review count (15% weight) - using relationship length
    try:
        review_count = len(destination.reviews) if hasattr(destination, 'reviews') and destination.reviews else 0
        if review_count > 0:
            # Normalize review count (max at 50 reviews = full score)
            review_score = min(review_count / 50.0, 1.0)
            score += review_score * 0.15
    except:
        # If reviews not loaded, skip this factor
        pass
    
    # Factor 3: Budget fit (20% weight)
    if budget_max and destination.price:
        if destination.price <= budget_max:
            # Within budget: full score
            score += 0.2
        elif destination.price <= budget_max * 1.2:
            # Slightly over: partial score
            score += 0.1
    else:
        score += 0.1  # Default if no budget constraint
    
    # Factor 4: Category preference match (15% weight)
    if user_prefs and user_prefs.preferred_categories:
        if destination.category in user_prefs.preferred_categories:
            score += 0.15
    else:
        score += 0.075  # Default
    
    # Factor 5: Weather conditions (20% weight) - NEW!
    if travel_dates and db:
        weather_score = await _calculate_weather_score(
            destination=destination,
            travel_dates=travel_dates,
            db=db
        )
        score += weather_score * 0.2
    else:
        score += 0.1  # Default if no travel dates provided
    
    return round(min(score, 1.0), 2)


async def _calculate_weather_score(
    destination: Destination,
    travel_dates: Dict,
    db: AsyncSession
) -> float:
    """
    Calculate weather score for destination based on travel dates.
    Returns: 0.0 - 1.0 score based on weather favorability.
    """
    try:
        # Parse travel dates
        start_date_str = travel_dates.get("start_date")
        end_date_str = travel_dates.get("end_date")
        
        if not start_date_str or not end_date_str:
            return 0.5  # Default neutral score if dates not provided
        
        # Convert strings to date objects
        if isinstance(start_date_str, str):
            start_date = datetime.fromisoformat(start_date_str).date()
        else:
            start_date = start_date_str
            
        if isinstance(end_date_str, str):
            end_date = datetime.fromisoformat(end_date_str).date()
        else:
            end_date = end_date_str
        
        # Query weather data for the destination during travel dates
        weather_query = select(Weather).where(
            and_(
                Weather.destination_id == destination.id,
                Weather.date >= start_date,
                Weather.date <= end_date
            )
        )
        result = await db.execute(weather_query)
        weather_records = result.scalars().all()
        
        if not weather_records:
            return 0.5  # Neutral score if no weather data available
        
        # Analyze weather conditions
        total_score = 0.0
        for weather in weather_records:
            # Build weather data dict for analyzer
            weather_data = {
                "temperature": weather.temperature_avg or weather.temperature_max or 25,
                "precipitation_probability": (weather.precipitation or 0) * 100 if weather.precipitation else 0,
                "condition": weather.condition or "unknown",
                "humidity": weather.humidity or 60
            }
            
            # Use weather analyzer to get score
            analysis = analyze_weather_for_travel(weather_data, [])
            total_score += analysis.get("weather_score", 0.5)
        
        # Average score across all days
        avg_score = total_score / len(weather_records) if weather_records else 0.5
        return round(avg_score, 2)
        
    except Exception as e:
        # Log error and return neutral score
        print(f"Warning: Error calculating weather score: {e}")
        return 0.5


def _generate_recommendation_reasoning(
    destination: Destination,
    confidence_score: float,
    budget_match: bool
) -> str:
    """Generate human-readable reasoning for recommendation."""
    reasons = []
    
    if destination.rating and destination.rating >= 4.0:
        reasons.append(f"highly rated ({destination.rating:.1f}/5.0)")
    
    review_count = len(destination.reviews) if destination.reviews else 0
    if review_count > 20:
        reasons.append(f"popular with {review_count} reviews")
    
    if budget_match:
        reasons.append("fits your budget")
    
    if destination.category:
        reasons.append(f"matches your interest in {destination.category}")
    
    if not reasons:
        reasons.append("recommended based on popularity")
    
    return f"Recommended because it's {', '.join(reasons)}."


async def get_user_recommendation_history(
    user_id: int,
    db: AsyncSession,
    limit: int = 50
) -> List[AIRecommendation]:
    """
    Get user's recommendation history.
    
    Args:
        user_id: ID of user
        db: Database session
        limit: Max results
        
    Returns:
        List of past recommendations
    """
    result = await db.execute(
        select(AIRecommendation)
        .options(selectinload(AIRecommendation.destination))
        .where(AIRecommendation.user_id == user_id)
        .order_by(AIRecommendation.created_at.desc())
        .limit(limit)
    )
    
    return list(result.scalars().all())


async def get_smart_itinerary_suggestions(
    user_id: int,
    destination_id: int,
    days: int,
    budget: float,
    db: AsyncSession
) -> Dict:
    """
    Get smart itinerary suggestions for a destination.
    Suggests activities, budget allocation, and timeline.
    
    Args:
        user_id: ID of user
        destination_id: ID of destination
        days: Number of days
        budget: Total budget
        db: Database session
        
    Returns:
        Dict with suggested itinerary structure
    """
    # Get destination
    dest_result = await db.execute(
        select(Destination).where(Destination.id == destination_id)
    )
    destination = dest_result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    # Budget allocation suggestions
    budget_per_day = budget / days if days > 0 else budget
    
    suggested_allocation = {
        "accommodation": budget_per_day * 0.4,  # 40% for accommodation
        "food": budget_per_day * 0.3,           # 30% for food
        "activities": budget_per_day * 0.2,     # 20% for activities
        "transport": budget_per_day * 0.1       # 10% for transport
    }
    
    # Activity suggestions (basic - can be enhanced with real data)
    suggested_activities = [
        {
            "day": i + 1,
            "morning": f"Explore {destination.name} morning attractions",
            "afternoon": f"Visit local {destination.category} sites",
            "evening": "Dinner and local experience",
            "estimated_cost": suggested_allocation["activities"]
        }
        for i in range(min(days, 7))  # Max 7 days of suggestions
    ]
    
    return {
        "destination": {
            "id": destination.id,
            "name": destination.name,
            "category": destination.category
        },
        "duration_days": days,
        "total_budget": budget,
        "budget_per_day": budget_per_day,
        "suggested_allocation": suggested_allocation,
        "suggested_activities": suggested_activities,
        "tips": [
            f"Best time to visit {destination.name} for optimal weather",
            f"Book accommodations early in {destination.city}",
            "Consider local transport passes for savings"
        ]
    }


def _calculate_confidence_score(
    destination: Destination,
    weather_data: Dict,
    budget_match: bool,
    rating: Optional[float]
) -> float:
    """
    Calculate confidence score based on multiple factors.
    
    Scoring breakdown:
    - Base score: 0.5
    - Weather score: 0-0.3 (based on weather_score from weather API)
    - Budget match: 0-0.2 (full points if within budget)
    - Rating: 0-0.2 (proportional to destination rating)
    
    Returns:
        Float between 0.0 and 1.0
    """
    base_score = 0.5
    
    # Weather scoring (0-0.3)
    # weather_score from Visual Crossing is 0-1 scale
    weather_score = weather_data.get("weather_score", 0.7) * 0.3
    
    # Budget match (0-0.2)
    budget_score = 0.2 if budget_match else 0
    
    # Rating (0-0.2)
    # Convert 0-5 rating to 0-0.2 scale
    rating_score = (rating / 5.0) * 0.2 if rating else 0.1
    
    # Calculate final score (max 1.0)
    final_score = base_score + weather_score + budget_score + rating_score
    
    return min(1.0, round(final_score, 2))

async def _enrich_with_flight_prices(
    recommendations: List[AIRecommendation],
    travel_dates: Dict[str, str],
    db: AsyncSession
):
    """
    Task 2.1: Enrich recommendations with live flight prices from Amadeus.
    Runs asynchronously in background to avoid blocking the response.
    Only checks top 3 recommendations for performance.
    
    Args:
        recommendations: List of recommendations to enrich
        travel_dates: Dict with start_date and end_date
        db: Database session
    """
    try:
        amadeus = get_amadeus_client()
        departure_date = travel_dates.get("start_date", "")
        return_date = travel_dates.get("end_date")
        
        # Extract just the date part if ISO datetime string
        if "T" in departure_date:
            departure_date = departure_date.split("T")[0]
        if return_date and "T" in return_date:
            return_date = return_date.split("T")[0]
        
        for rec in recommendations:
            try:
                # Default origin: Jakarta (CGK) - most common departure point
                origin_code = "CGK"
                
                # Destination: Bali airports (DPS for Denpasar is most common)
                destination_code = "DPS"
                
                # Search for cheapest flight
                print(f"[FLIGHT PRICE] Checking flights {origin_code} -> {destination_code} on {departure_date}")
                
                flight_offers = await amadeus.search_flights(
                    origin=origin_code,
                    destination=destination_code,
                    departure_date=departure_date,
                    return_date=return_date,
                    adults=1,
                    travel_class="ECONOMY",
                    max_results=5  # Get top 5 to find cheapest
                )
                
                if flight_offers and len(flight_offers) > 0:
                    # Find cheapest offer
                    cheapest = min(
                        flight_offers,
                        key=lambda x: float(x.get("price", {}).get("total", float('inf')))
                    )
                    
                    price_data = cheapest.get("price", {})
                    total_price = float(price_data.get("total", 0))
                    currency = price_data.get("currency", "IDR")
                    
                    # Add to reasoning
                    if not rec.reasoning:
                        rec.reasoning = {}
                    
                    rec.reasoning["live_flight_price"] = {
                        "amount": total_price,
                        "currency": currency,
                        "route": f"{origin_code} → {destination_code}",
                        "departure_date": departure_date,
                        "return_date": return_date,
                        "checked_at": datetime.utcnow().isoformat(),
                        "is_round_trip": bool(return_date)
                    }
                    
                    print(f"[FLIGHT PRICE] Found: {currency} {total_price:,.0f}")
                    
                    # Update in database
                    await db.commit()
                else:
                    print(f"[FLIGHT PRICE] No flights found for {origin_code} -> {destination_code}")
                    
            except Exception as e:
                print(f"[FLIGHT PRICE ERROR] Failed to get price for recommendation {rec.id}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"[FLIGHT PRICE ERROR] Failed to initialize Amadeus client: {str(e)}")