from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from src.accommodation.models import AccommodationSearch, AccommodationRecommendation
from src.accommodation.schemas import AccommodationSearchRequest
from src.itinerary.models import Itinerary
from utils.amadeus_client import get_amadeus_client
from datetime import datetime
import random


async def search_accommodations(user_id: int, data: AccommodationSearchRequest, db: AsyncSession):
    """
    Search accommodations using Amadeus Hotel API with fallback to mock data
    """
    print(f"\n[ACCOMMODATION] ====== NEW SEARCH REQUEST ======")
    print(f"[ACCOMMODATION] Location: {data.location}, Guests: {data.guests}")
    print(f"[ACCOMMODATION] Check-in: {data.check_in}, Check-out: {data.check_out}")
    
    # Strip timezone info to match DB columns (DateTime without timezone)
    check_in_naive = data.check_in.replace(tzinfo=None) if data.check_in else None
    check_out_naive = data.check_out.replace(tzinfo=None) if data.check_out else None
    
    search_record = AccommodationSearch(
        user_id=user_id,
        location=data.location,
        check_in=check_in_naive,
        check_out=check_out_naive,
        guests=data.guests,
        max_price=data.max_price,
        min_rating=data.min_rating,
        amenities=data.amenities
    )
    db.add(search_record)
    
    # Calculate number of nights
    nights = (data.check_out - data.check_in).days
    if nights <= 0:
        nights = 1
    
    recommendations = []
    
    # Use real Amadeus API data
    use_mock_data = False  # Set to True to use mock data for demo
    
    if not use_mock_data:
        try:
            # Try to get real accommodation data from Amadeus API
            print(f"[ACCOMMODATION] Fetching REAL data from Amadeus API for {data.location}")
            amadeus = get_amadeus_client()
            
            # Convert location to city code
            # All Bali areas map to DPS (Denpasar/Bali airport code)
            city_codes = {
                # General Bali
                "bali": "DPS",
                "denpasar": "DPS",
                # Popular areas in Bali
                "ubud": "DPS",
                "seminyak": "DPS",
                "nusa dua": "DPS",
                "sanur": "DPS",
                "canggu": "DPS",
                # Bali regencies (Kabupaten) and city
                "kota denpasar": "DPS",
                "kabupaten badung": "DPS",
                "kabupaten gianyar": "DPS",
                "kabupaten tabanan": "DPS",
                "kabupaten buleleng": "DPS",
                "kabupaten karangasem": "DPS",
                "kabupaten klungkung": "DPS",
                "kabupaten bangli": "DPS",
                "kabupaten jembrana": "DPS",
                # Other Indonesian cities
                "jakarta": "JKT",
                "surabaya": "SUB",
                "yogyakarta": "JOG",
                "bandung": "BDO"
            }
            
            city_code = city_codes.get(data.location.lower(), "DPS")
            
            # Convert dates to strings
            check_in_str = data.check_in.strftime("%Y-%m-%d")
            check_out_str = data.check_out.strftime("%Y-%m-%d")
            
            # Prepare ratings filter
            ratings = None
            if data.min_rating:
                ratings = [int(data.min_rating), int(data.min_rating) + 1, 5]
            
            # Search hotels with Amadeus
            print(f"[ACCOMMODATION] Calling Amadeus API: city_code={city_code}, check_in={check_in_str}, check_out={check_out_str}")
            
            amadeus_results = await amadeus.search_hotels_by_city(
                city_code=city_code,
                check_in_date=check_in_str,
                check_out_date=check_out_str,
                adults=data.guests,
                radius=50,
                ratings=ratings,
                max_results=15
            )
            
            print(f"[ACCOMMODATION] Amadeus API returned {len(amadeus_results) if amadeus_results else 0} hotels")
            
            # Process Amadeus results
            for idx, hotel_data in enumerate(amadeus_results[:15]):
                try:
                    hotel_name = hotel_data.get("name", f"Hotel {idx + 1}")
                    
                    # Get geolocation
                    geo = hotel_data.get("geoCode", {})
                    latitude = geo.get("latitude", random.uniform(-8.8, -8.1))
                    longitude = geo.get("longitude", random.uniform(114.5, 115.6))
                    
                    # Get rating (convert from Amadeus format)
                    rating_value = hotel_data.get("rating")
                    if rating_value:
                        # Amadeus uses 1-5 scale
                        rating = float(rating_value)
                    else:
                        rating = random.uniform(3.5, 4.8)
                    
                    # Get offer/pricing if available
                    offer = hotel_data.get("offer", {})
                    
                    if offer and "price" in offer:
                        price_info = offer["price"]
                        total_price_str = price_info.get("total", "0")
                        total_price = int(float(total_price_str))
                        price_per_night = total_price // nights if nights > 0 else total_price
                    else:
                        # Estimate pricing if not available
                        base_price = random.randint(200000, 2000000)
                        price_per_night = base_price
                        total_price = price_per_night * nights
                    
                    # Budget compatibility
                    budget_compatible = True
                    if data.max_price and total_price > data.max_price:
                        budget_compatible = False
                        if not data.use_ai_recommendations:
                            continue
                    
                    # Calculate recommendation score
                    score = rating / 5.0
                    if data.max_price:
                        budget_efficiency = 1 - (total_price / data.max_price) if total_price <= data.max_price else 0.5
                        score = (score + budget_efficiency) / 2
                    
                    # Get amenities
                    available_amenities = offer.get("room", {}).get("typeEstimated", {}).get("bedType") or []
                    if isinstance(available_amenities, str):
                        available_amenities = [available_amenities]
                    if not available_amenities:
                        available_amenities = data.amenities or ["WiFi", "AC", "Breakfast"]
                    
                    # Build description
                    description = hotel_data.get("description") or f"Located in {data.location}, this hotel offers comfortable accommodations with modern amenities."
                    
                    # Generate hotel image URL based on hotel characteristics
                    # Use Unsplash hotel images with specific query to get variety
                    hotel_type = "luxury" if price_per_night > 1000000 else "resort" if price_per_night > 500000 else "hotel"
                    image_urls = [
                        f"https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",  # Luxury hotel
                        f"https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80",  # Hotel room
                        f"https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",  # Hotel exterior
                        f"https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&q=80",  # Resort pool
                        f"https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800&q=80",  # Hotel lobby
                        f"https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80",  # Beach resort
                        f"https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&q=80",  # Modern hotel
                        f"https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800&q=80",  # Pool villa
                    ]
                    image_url = image_urls[idx % len(image_urls)]
                    
                    recommendation_reason = f"Rated {rating:.1f}/5"
                    if budget_compatible:
                        recommendation_reason += f" - Fits your budget"
                    
                    recommendation = AccommodationRecommendation(
                        user_id=user_id,
                        hotel_name=hotel_name,
                        location=data.location,
                        latitude=latitude,
                        longitude=longitude,
                        price_per_night=price_per_night,
                        total_price=total_price,
                        rating=round(rating, 1),
                        amenities=available_amenities,
                        description=description,
                        image_url=image_url,
                        recommendation_score=round(score, 2),
                        recommendation_reason=recommendation_reason,
                        budget_compatible=budget_compatible,
                        weather_compatible=True
                    )
                    db.add(recommendation)
                    recommendations.append(recommendation)
                    
                except Exception as e:
                    print(f"Error processing Amadeus hotel result: {e}")
                    continue
            
            # If we got results from Amadeus, use them
            if recommendations:
                print(f"[ACCOMMODATION] ✓ Using {len(recommendations)} REAL hotels from Amadeus API")
                search_record.search_results_count = len(recommendations)
                await db.commit()
                return recommendations
                    
        except Exception as e:
            import traceback
            print(f"[ACCOMMODATION] ✗ Amadeus API ERROR: {type(e).__name__}: {e}")
            print(f"[ACCOMMODATION] Stack trace:")
            traceback.print_exc()
            print(f"[ACCOMMODATION] Falling back to mock data")
    
    # Fallback to mock data if Amadeus fails (or if demo mode enabled)
    print(f"\n[ACCOMMODATION] ⚠️  USING MOCK/DUMMY DATA (Amadeus API failed or disabled)")
    sample_hotels = [
        {
            "name": "Four Seasons Resort Bali at Jimbaran Bay",
            "base_price": 754685,
            "rating": 4.8,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80"
        },
        {
            "name": "The Mulia Bali",
            "base_price": 680000,
            "rating": 4.7,
            "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&q=80"
        },
        {
            "name": "COMO Uma Canggu",
            "base_price": 520000,
            "rating": 4.5,
            "image": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80"
        },
        {
            "name": "Grand Hyatt Bali",
            "base_price": 850000,
            "rating": 4.7,
            "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80"
        },
        {
            "name": "Alila Villas Uluwatu",
            "base_price": 1200000,
            "rating": 4.9,
            "image": "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&q=80"
        },
        {
            "name": "Padma Resort Legian",
            "base_price": 450000,
            "rating": 4.3,
            "image": "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800&q=80"
        },
        {
            "name": "The St. Regis Bali Resort",
            "base_price": 1500000,
            "rating": 4.8,
            "image": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80"
        },
        {
            "name": "Karma Kandara Resort",
            "base_price": 980000,
            "rating": 4.6,
            "image": "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800&q=80"
        },
        {
            "name": "Bulgari Resort Bali",
            "base_price": 2200000,
            "rating": 4.9,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80"
        },
        {
            "name": "Mandapa Ritz-Carlton Reserve",
            "base_price": 1800000,
            "rating": 4.9,
            "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&q=80"
        },
        {
            "name": "W Bali - Seminyak",
            "base_price": 750000,
            "rating": 4.5,
            "image": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80"
        },
        {
            "name": "Sofitel Bali Nusa Dua Beach Resort",
            "base_price": 620000,
            "rating": 4.4,
            "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80"
        },
    ]
    
    # Add price variation to make each search unique
    for hotel in sample_hotels:
        price_per_night = hotel["base_price"] + random.randint(-50000, 50000)  # ±50k variation
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
            image_url=hotel.get("image", "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80"),
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

