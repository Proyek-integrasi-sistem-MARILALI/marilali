from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from src.transportation.models import FlightSearch, FlightRecommendation
from src.transportation.schemas import FlightSearchRequest
from utils.amadeus_client import get_amadeus_client
from datetime import timedelta, datetime
import random


async def search_flights(user_id: int, data: FlightSearchRequest, db: AsyncSession):
    """
    Search flights using Amadeus API with fallback to mock data
    """
    # Save search history (strip timezone info to match DB columns)
    departure_date_naive = data.departure_date.replace(tzinfo=None) if data.departure_date else None
    return_date_naive = data.return_date.replace(tzinfo=None) if data.return_date else None
    
    search_record = FlightSearch(
        user_id=user_id,
        origin=data.origin,
        destination=data.destination,
        departure_date=departure_date_naive,
        return_date=return_date_naive,
        passengers=data.passengers,
        cabin_class=data.cabin_class,
        max_price=data.max_price
    )
    db.add(search_record)
    
    recommendations = []
    
    # Use real Amadeus API data
    use_mock_data = False  # Set to True to use mock data for demo
    
    if not use_mock_data:
        try:
            # Try to get real flight data from Amadeus
            print(f"[TRANSPORTATION] Fetching REAL data from Amadeus API: {data.origin} -> {data.destination}")
            amadeus = get_amadeus_client()
        
            # Convert city names to airport codes if needed
            # Common Indonesian airports
            airport_codes = {
                "jakarta": "CGK",
                "bali": "DPS",
                "denpasar": "DPS",
                "surabaya": "SUB",
                "yogyakarta": "JOG",
                "medan": "KNO",
                "bandung": "BDO"
            }
            
            origin_code = airport_codes.get(data.origin.lower(), data.origin.upper())
            dest_code = airport_codes.get(data.destination.lower(), data.destination.upper())
            
            # Search flights with Amadeus
            departure_date_str = data.departure_date.strftime("%Y-%m-%d")
            return_date_str = data.return_date.strftime("%Y-%m-%d") if data.return_date else None
            
            travel_class_map = {
                "economy": "ECONOMY",
                "business": "BUSINESS",
                "first": "FIRST"
            }
            
            amadeus_results = await amadeus.search_flights(
                origin=origin_code,
                destination=dest_code,
                departure_date=departure_date_str,
                adults=data.passengers,
                return_date=return_date_str,
                travel_class=travel_class_map.get(data.cabin_class, "ECONOMY"),
                max_results=10
            )
            
            # Process Amadeus results
            for idx, flight_offer in enumerate(amadeus_results[:10]):
                try:
                    # Extract flight details from Amadeus response
                    itinerary = flight_offer.get("itineraries", [{}])[0]
                    segments = itinerary.get("segments", [])
                    
                    if not segments:
                        continue
                    
                    first_segment = segments[0]
                    last_segment = segments[-1]
                    
                    # Extract pricing
                    price_info = flight_offer.get("price", {})
                    total_price = float(price_info.get("total", 0))
                    
                    # Convert to IDR if needed (Amadeus returns in requested currency)
                    price_idr = int(total_price)
                    
                    # Calculate duration
                    departure_time = datetime.fromisoformat(first_segment["departure"]["at"].replace("Z", "+00:00"))
                    arrival_time = datetime.fromisoformat(last_segment["arrival"]["at"].replace("Z", "+00:00"))
                    duration_minutes = int((arrival_time - departure_time).total_seconds() / 60)
                    
                    # Strip timezone info to match DB column (DateTime without timezone)
                    departure_time = departure_time.replace(tzinfo=None)
                    arrival_time = arrival_time.replace(tzinfo=None)
                    
                    # Get airline info
                    airline_code = first_segment["carrierCode"]
                    flight_number = f"{airline_code}{first_segment['number']}"
                    
                    # Map airline codes to names
                    airline_names = {
                        "GA": "Garuda Indonesia",
                        "QZ": "AirAsia",
                        "JT": "Lion Air",
                        "ID": "Batik Air",
                        "QG": "Citilink"
                    }
                    airline_name = airline_names.get(airline_code, airline_code)
                    
                    # Calculate stops
                    stops = len(segments) - 1
                    
                    # Budget compatibility
                    budget_compatible = True
                    if data.max_price and price_idr > data.max_price:
                        budget_compatible = False
                    
                    # Calculate recommendation score
                    score = 0.7  # Base score for real data
                    if stops == 0:
                        score += 0.2
                    if budget_compatible:
                        score += 0.1
                    
                    recommendation_reason = f"{airline_name} - "
                    if stops == 0:
                        recommendation_reason += "Direct flight, "
                    else:
                        recommendation_reason += f"{stops} stop(s), "
                    recommendation_reason += f"{duration_minutes // 60}h {duration_minutes % 60}m"
                    
                    recommendation = FlightRecommendation(
                        user_id=user_id,
                        airline=airline_name,
                        flight_number=flight_number,
                        origin=first_segment["departure"]["iataCode"],
                        destination=last_segment["arrival"]["iataCode"],
                        departure_time=departure_time,
                        arrival_time=arrival_time,
                        duration_minutes=duration_minutes,
                        stops=stops,
                        cabin_class=data.cabin_class,
                        price=price_idr,
                        baggage_allowance="Varies by airline",
                        recommendation_score=round(score, 2),
                        recommendation_reason=recommendation_reason,
                        budget_compatible=budget_compatible,
                        weather_optimized=True
                    )
                    db.add(recommendation)
                    recommendations.append(recommendation)
                    
                except Exception as e:
                    print(f"Error processing Amadeus flight result: {e}")
                    continue
            
            # If we got results from Amadeus, use them
            if recommendations:
                print(f"[TRANSPORTATION] ✓ Using {len(recommendations)} REAL flights from Amadeus API")
                search_record.search_results_count = len(recommendations)
                await db.commit()
                return recommendations
                
        except Exception as e:
            print(f"[TRANSPORTATION] ✗ Amadeus API error, falling back to mock data: {e}")
    
    # Fallback to mock data if Amadeus fails or returns no results (or if demo mode enabled)
    airlines = [
        {"name": "Garuda Indonesia", "code": "GA", "price_range": (1800000, 2800000)},
        {"name": "Air Asia", "code": "QZ", "price_range": (800000, 1500000)},
        {"name": "Lion Air", "code": "JT", "price_range": (900000, 1600000)},
        {"name": "Citilink", "code": "QG", "price_range": (1000000, 1700000)},
        {"name": "Batik Air", "code": "ID", "price_range": (1500000, 2500000)},
    ]
    
    for i, airline_info in enumerate(airlines):
        airline = airline_info["name"]
        airline_code = airline_info["code"]
        price_min, price_max = airline_info["price_range"]
        
        # Generate varied flight details
        base_price = random.randint(price_min, price_max)
        duration = random.randint(60, 480)  # minutes
        stops = random.choice([0, 0, 1])  # More direct flights
        
        # Add variation based on time of day
        hour = random.choice([6, 8, 10, 13, 15, 18, 20])
        if hour in [6, 20]:  # Early morning or late evening - cheaper
            base_price = int(base_price * 0.85)
        elif hour in [10, 15]:  # Peak hours - more expensive
            base_price = int(base_price * 1.15)
        
        # Adjust price based on cabin class
        class_multiplier = {"economy": 1.0, "business": 2.5, "first": 4.0}
        price = int(base_price * class_multiplier.get(data.cabin_class, 1.0))
        
        # Multiply by number of passengers
        total_price = price * data.passengers
        
        # Multiply by number of passengers
        total_price = price * data.passengers
        
        # Apply budget filter
        budget_compatible = True
        if data.max_price and total_price > data.max_price:
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
            budget_efficiency = 1 - (total_price / data.max_price) if total_price <= data.max_price else 0.3
            score = (score + budget_efficiency) / 2
        
        # Use naive datetime (strip timezone if present) to match DB columns
        base_departure = departure_date_naive if departure_date_naive else data.departure_date.replace(tzinfo=None)
        departure_time = base_departure.replace(hour=hour, minute=random.randint(0, 59))
        arrival_time = departure_time + timedelta(minutes=duration)
        
        # Generate unique flight number
        flight_number = f"{airline_code}{random.randint(1000, 9999)}"
        
        # Generate unique flight number
        flight_number = f"{airline_code}{random.randint(1000, 9999)}"
        
        recommendation_reason = f"{airline} - "
        if stops == 0:
            recommendation_reason += "Direct flight, "
        recommendation_reason += f"{duration // 60}h {duration % 60}m duration"
        if budget_compatible:
            recommendation_reason += f", fits within budget"
        
        recommendation = FlightRecommendation(
            user_id=user_id,
            airline=airline,
            flight_number=flight_number,
            origin=data.origin,
            destination=data.destination,
            departure_time=departure_time,
            arrival_time=arrival_time,
            duration_minutes=duration,
            stops=stops,
            cabin_class=data.cabin_class,
            price=total_price,  # Use total price including all passengers
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
