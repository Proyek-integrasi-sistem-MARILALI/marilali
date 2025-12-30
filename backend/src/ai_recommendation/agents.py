import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from langbase import Langbase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Dict, Optional, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database import AsyncSessionLocal
from src.user.models import User  # Import User first to avoid circular import
from src.destination.models import Destination
from src.weather.weather_models import Weather
from src.weather.visual_crossing_weather import VisualCrossingWeatherService
from src.review.models import Review  # Import to resolve relationship
from src.favorite.models import FavoriteDestination  # Import to resolve relationship
from utils.weather_analyzer import analyze_weather_for_travel

# Load environment variables
load_dotenv()

async def get_travel_recommendations(
    user_query: str,
    db: AsyncSession,
    travel_dates: Optional[Dict[str, str]] = None,
    budget_max: Optional[float] = None,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Retrieve travel recommendations from Langbase memory with weather context.
    
    Args:
        user_query: User's travel-related question or preference
        db: Database session for querying destinations and weather
        travel_dates: Dict with 'start_date' and 'end_date' (ISO format strings)
        budget_max: Maximum budget filter
        top_k: Number of recommendations to retrieve
    
    Returns:
        Dict with destinations, weather context, and recommendations
    """
    if not os.getenv('LANGBASE_API_KEY'):
        print('❌ Missing LANGBASE_API_KEY in environment variables.')
        return None

    # Initialize Langbase client
    langbase = Langbase(api_key=os.getenv('LANGBASE_API_KEY'))

    # Step 1: Retrieve relevant destinations from Langbase memory
    print(f"\n[SEARCH] Searching for: {user_query}")
    
    memory_response = langbase.memories.retrieve(
        memory=[{'name': 'bali-travel-cohere-light'}],
        query=user_query,
        top_k=top_k
    )

    print("\n[OK] Retrieved destinations from Langbase memory")
    
    # Step 2: Extract destination data from memory response
    destinations_data = _extract_destination_names(memory_response)
    
    if not destinations_data:
        print("[WARNING] No destination data found in memory response")
        return {
            "memory_response": memory_response,
            "destinations": [],
            "weather_context": {},
            "recommendations": [],
            "query": user_query
        }
    
    # Step 3: Query database for full destination details (or create if missing)
    destinations = await _fetch_destinations_from_db(destinations_data, db, budget_max)
    
    # Step 4: Fetch weather data for travel dates
    weather_context = {}
    if travel_dates and destinations:
        weather_context = await _fetch_weather_for_destinations(
            destinations=destinations,
            travel_dates=travel_dates,
            db=db
        )
        print(f"\n[WEATHER] Fetched weather for {len(weather_context)} destinations")
    
    # Step 5: Build enriched recommendations
    recommendations = _build_recommendations(
        destinations=destinations,
        weather_context=weather_context,
        travel_dates=travel_dates
    )
    
    return {
        "memory_response": memory_response,
        "destinations": [{
            "id": d.id,
            "name": d.name,
            "category": d.category,
            "location": d.location,
            "price": d.price,
            "rating": d.rating,
            "description": d.description
        } for d in destinations],
        "weather_context": weather_context,
        "recommendations": recommendations,
        "query": user_query
    }

def _extract_destination_names(memory_response: Any) -> List[Dict[str, Any]]:
    """
    Extract destination data from Langbase memory response.
    Langbase returns CSV data from uploaded file.
    CSV Format: Place,Location,Coordinate,Google Maps Rating,Google Reviews (Count),Source,Description,Tourism/Visitor Fee (approx in USD)
    Returns list of dicts with destination information.
    """
    destinations_data = []
    seen_names = set()
    
    try:
        # Langbase returns a list of documents with 'text' field containing CSV data
        if isinstance(memory_response, list):
            for item in memory_response:
                if isinstance(item, dict) and 'text' in item:
                    text = item['text']
                    # Parse CSV-like text
                    lines = text.strip().split('\n')
                    for line in lines:
                        # Skip header or empty lines
                        if not line or line.startswith('Place,'):
                            continue
                        
                        # Split by comma but handle quoted fields
                        import csv
                        import io
                        reader = csv.reader(io.StringIO(line))
                        try:
                            parts = next(reader)
                        except:
                            continue
                        
                        if len(parts) >= 4:
                            place_name = parts[0].strip()
                            if place_name and place_name not in seen_names:
                                seen_names.add(place_name)
                                
                                location = parts[1].strip() if len(parts) > 1 else 'Bali'
                                rating_str = parts[3].strip() if len(parts) > 3 else None
                                description = parts[6].strip() if len(parts) > 6 else ''
                                fee_str = parts[7].strip() if len(parts) > 7 else ''
                                
                                # Parse rating
                                rating = None
                                if rating_str:
                                    try:
                                        rating = float(rating_str)
                                    except:
                                        rating = 4.0
                                
                                # Parse entrance fee and convert USD to IDR (~Rp 15,700 per USD)
                                price = 0
                                if fee_str and 'yes' in fee_str.lower():
                                    # Extract price from text
                                    import re
                                    # Look for IDR/Rupiah amounts first
                                    idr_match = re.search(r'(?:IDR|Rp|Rupiah)\s*\.?\s*([\d,]+)', fee_str, re.IGNORECASE)
                                    if idr_match:
                                        price_str = idr_match.group(1).replace(',', '')
                                        try:
                                            price = int(price_str)
                                        except:
                                            price = 0
                                    else:
                                        # Look for USD amount and convert
                                        usd_match = re.search(r'\$?\s*([\d.]+)\s*USD', fee_str, re.IGNORECASE)
                                        if usd_match:
                                            usd_price = float(usd_match.group(1))
                                            price = int(usd_price * 15700)  # Convert to IDR
                                
                                # Determine category from place name or description
                                category = 'attraction'
                                name_lower = place_name.lower()
                                desc_lower = description.lower()
                                if 'temple' in name_lower or 'pura' in name_lower or 'temple' in desc_lower:
                                    category = 'temple'
                                elif 'beach' in name_lower or 'beach' in desc_lower:
                                    category = 'beach'
                                elif 'waterfall' in name_lower:
                                    category = 'waterfall'
                                elif 'rice' in name_lower and 'terrace' in name_lower:
                                    category = 'rice_terrace'
                                elif 'park' in name_lower or 'zoo' in name_lower:
                                    category = 'park'
                                elif 'market' in name_lower:
                                    category = 'market'
                                elif 'museum' in name_lower or 'monument' in name_lower:
                                    category = 'cultural'
                                
                                destinations_data.append({
                                    'name': place_name,
                                    'category': category,
                                    'location': location,
                                    'description': description,
                                    'price': price,
                                    'rating': rating
                                })
        
        print(f"[OK] Extracted {len(destinations_data)} destination data: {[d['name'] for d in destinations_data[:5]]}")
    
    except Exception as e:
        print(f"[WARNING] Error extracting destination data: {e}")
        import traceback
        traceback.print_exc()
    
    return destinations_data[:10]  # Limit to top 10


async def _fetch_destinations_from_db(
    destinations_data: List[Dict[str, Any]],
    db: AsyncSession,
    budget_max: Optional[float] = None
) -> List[Destination]:
    """
    Query database for destinations matching names from memory.
    If not found, create them from Langbase data.
    """
    destinations = []
    
    try:
        for dest_data in destinations_data:
            dest_name = dest_data['name']
            
            # Try to find existing destination
            query = select(Destination).where(
                or_(
                    Destination.name == dest_name,
                    Destination.name.ilike(f"%{dest_name}%")
                )
            )
            result = await db.execute(query)
            destination = result.scalar_one_or_none()
            
            if destination:
                print(f"[OK] Found existing: {destination.name}")
            else:
                # Create new destination from Langbase data
                print(f"[CREATE] Creating destination: {dest_name}")
                destination = Destination(
                    name=dest_name,
                    category=dest_data.get('category', 'attraction'),
                    location=dest_data.get('location', 'Bali'),
                    address=dest_data.get('location', 'Bali'),
                    city='Bali',
                    country='Indonesia',
                    price=dest_data.get('price', 0),
                    rating=dest_data.get('rating', 4.0),
                    description=dest_data.get('description', ''),
                    source='langbase',
                    created_at=datetime.utcnow()
                )
                db.add(destination)
                await db.flush()  # Get ID without committing
                await db.refresh(destination)
            
            # Apply budget filter
            if budget_max and destination.price and destination.price > budget_max:
                continue
            
            destinations.append(destination)
        
        # Commit all new destinations
        await db.commit()
        
        print(f"[OK] Found {len(destinations)} matching destinations in database")
        
        return destinations
    
    except Exception as e:
        print(f"[ERROR] Error fetching/creating destinations: {e}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        return []


async def _fetch_weather_for_destinations(
    destinations: List[Destination],
    travel_dates: Dict[str, str],
    db: AsyncSession
) -> Dict[int, Dict]:
    """
    Fetch real-time weather data from Visual Crossing API for destinations during travel dates.
    Returns dict mapping destination_id to weather analysis.
    """
    weather_context = {}
    
    try:
        start_date_str = travel_dates.get("start_date")
        end_date_str = travel_dates.get("end_date")
        
        if not start_date_str or not end_date_str:
            print("[WEATHER] Missing travel dates")
            return weather_context
        
        # Parse dates
        start_date = datetime.fromisoformat(start_date_str).date()
        end_date = datetime.fromisoformat(end_date_str).date()
        
        # Initialize weather service
        weather_service = VisualCrossingWeatherService()
        
        print(f"[WEATHER] Fetching real-time weather for {len(destinations)} destinations from {start_date} to {end_date}")
        
        for destination in destinations:
            try:
                # Use location for weather API (city name or coordinates)
                location = destination.location or destination.city or "Bali"
                
                print(f"[WEATHER] Fetching for {destination.name} at {location}")
                
                # Fetch forecast from Visual Crossing API
                weather_data = await weather_service.get_forecast(
                    location=location,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not weather_data:
                    print(f"[WEATHER] No data returned for {destination.name}")
                    continue
                
                # Extract daily forecasts
                daily_forecasts = weather_data.get("days", [])
                
                if not daily_forecasts:
                    print(f"[WEATHER] No daily forecasts for {destination.name}")
                    continue
                
                # Build weather data list for analyzer
                weather_data_list = []
                for day in daily_forecasts:
                    weather_day = {
                        "temperature": day.get("temp", 25),
                        "temperature_max": day.get("tempmax", 30),
                        "temperature_min": day.get("tempmin", 20),
                        "precipitation_probability": day.get("precip", 0),
                        "condition": day.get("conditions", "unknown"),
                        "humidity": day.get("humidity", 60),
                        "windspeed": day.get("windspeed", 0),
                        "description": day.get("description", ""),
                        "date": day.get("datetime", "")
                    }
                    weather_data_list.append(weather_day)
                
                # Calculate weather score (0-1 scale)
                # Good weather: 20-32°C, low precipitation, favorable conditions
                avg_temp = sum(d["temperature"] for d in weather_data_list) / len(weather_data_list)
                avg_precip = sum(d["precipitation_probability"] for d in weather_data_list) / len(weather_data_list)
                
                # Temperature score (optimal: 20-32°C)
                temp_score = 1.0
                if avg_temp < 20:
                    temp_score = max(0.3, 1.0 - (20 - avg_temp) / 10)
                elif avg_temp > 32:
                    temp_score = max(0.3, 1.0 - (avg_temp - 32) / 10)
                
                # Precipitation score (optimal: < 30%)
                precip_score = max(0.0, 1.0 - (avg_precip / 100))
                
                # Combined weather score
                weather_score = (temp_score * 0.6) + (precip_score * 0.4)
                
                # Determine if favorable
                is_favorable = weather_score > 0.6
                
                print(f"[WEATHER] {destination.name}: temp={avg_temp:.1f}°C, precip={avg_precip:.1f}%, score={weather_score:.2f}")
                
                weather_context[destination.id] = {
                    "forecast": weather_data_list,
                    "is_favorable": is_favorable,
                    "weather_score": round(weather_score, 2),
                    "avg_temperature": round(avg_temp, 1),
                    "avg_precipitation": round(avg_precip, 1),
                    "summary": f"{'Favorable' if is_favorable else 'Less favorable'} weather conditions"
                }
                
            except Exception as e:
                print(f"[WARNING] Error fetching weather for {destination.name}: {e}")
                continue
        
        print(f"[WEATHER] Successfully fetched weather for {len(weather_context)} destinations")
    
    except Exception as e:
        print(f"[ERROR] Error in weather fetching: {e}")
        import traceback
        traceback.print_exc()
    
    return weather_context


def _build_recommendations(
    destinations: List[Destination],
    weather_context: Dict[int, Dict],
    travel_dates: Optional[Dict]
) -> List[Dict]:
    """
    Build final recommendations with weather and scoring.
    Enhanced scoring: Rating (40%) + Weather (50%) + Popularity (10%)
    """
    recommendations = []
    
    for destination in destinations:
        weather_info = weather_context.get(destination.id, {})
        
        # Calculate comprehensive score
        rating_score = 0.0
        weather_score = 0.0
        popularity_score = 0.0
        
        # Rating score (40% weight) - normalized to 0-1
        if destination.rating:
            rating_score = (destination.rating / 5.0) * 0.4
        
        # Weather score (50% weight) - use real-time weather data
        if weather_info and weather_info.get("weather_score"):
            weather_score = weather_info.get("weather_score", 0.5) * 0.5
        else:
            # Default to moderate score if no weather data
            weather_score = 0.25
        
        # Popularity score (10% weight) - based on review count if available
        # This is a placeholder - you might want to add review_count to the destination model
        popularity_score = 0.05  # Default baseline
        
        # Total confidence score
        total_score = rating_score + weather_score + popularity_score
        
        recommendations.append({
            "destination": destination,  # Include the full destination object
            "destination_id": destination.id,
            "destination_name": destination.name,
            "category": destination.category,
            "price": destination.price,
            "rating": destination.rating,
            "confidence_score": round(total_score, 2),
            "reasoning": {
                "score": round(total_score, 2),
                "score_breakdown": {
                    "rating_score": round(rating_score, 2),
                    "weather_score": round(weather_score, 2),
                    "popularity_score": round(popularity_score, 2)
                },
                "weather_context": weather_info if weather_info else None,
                "weather_favorable": weather_info.get("is_favorable", None) if weather_info else None,
                "avg_temperature": weather_info.get("avg_temperature") if weather_info else None,
                "avg_precipitation": weather_info.get("avg_precipitation") if weather_info else None
            }
        })
    
    # Sort by confidence score
    recommendations.sort(key=lambda x: x["confidence_score"], reverse=True)
    
    return recommendations


async def main():
    # Example usage with database
    from src.database import AsyncSessionLocal
    
    query = "What are the best temples to visit in Bali?"
    travel_dates = {
        "start_date": "2025-25-01",
        "end_date": "2026-01-01"
    }
    
    async with AsyncSessionLocal() as db:
        result = await get_travel_recommendations(
            user_query=query,
            db=db,
            travel_dates=travel_dates,
            budget_max=100.0,
            top_k=5
        )
        
        if result:
            print("\n[RECOMMENDATIONS] AI-Powered Recommendations with Weather Context:")
            print(f"\nQuery: {result['query']}")
            print(f"\nFound {len(result['destinations'])} destinations")
            
            for rec in result['recommendations']:
                print(f"\n* {rec['destination_name']}")
                print(f"   Category: {rec['category']}")
                print(f"   Price: ${rec['price']}")
                print(f"   Rating: {rec['rating']}/5.0")
                print(f"   Confidence Score: {rec['confidence_score']}")
                print(f"   Weather Favorable: {'YES' if rec['weather_favorable'] else 'CAUTION'}")
                if rec['weather_warnings']:
                    print(f"   Weather Warnings: {', '.join(rec['weather_warnings'])}")
                if rec['best_activities']:
                    print(f"   Best Activities: {', '.join(rec['best_activities'])}")

if __name__ == '__main__':
    asyncio.run(main())
