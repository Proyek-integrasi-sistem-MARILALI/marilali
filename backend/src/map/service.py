"""
Map service for location and route operations.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from src.map.models import SavedLocation, RouteCache
from src.map.schemas import LocationCreate, RouteRequest
import math


async def save_location(user_id: int, data: LocationCreate, db: AsyncSession):
    """Save a location for a user."""
    location = SavedLocation(
        user_id=user_id,
        name=data.name,
        address=data.address,
        latitude=data.latitude,
        longitude=data.longitude,
        place_type=data.place_type,
        notes=data.notes
    )
    db.add(location)
    await db.commit()
    await db.refresh(location)
    return location


async def get_user_locations(user_id: int, db: AsyncSession):
    """Get all saved locations for a user."""
    result = await db.execute(
        select(SavedLocation).where(SavedLocation.user_id == user_id)
    )
    return result.scalars().all()


async def delete_location(location_id: int, user_id: int, db: AsyncSession):
    """Delete a saved location."""
    result = await db.execute(
        select(SavedLocation).where(
            SavedLocation.id == location_id,
            SavedLocation.user_id == user_id
        )
    )
    location = result.scalar_one_or_none()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    await db.delete(location)
    await db.commit()
    return {"message": "Location deleted successfully"}


async def calculate_route(data: RouteRequest, db: AsyncSession):
    """Calculate route between two points."""
    # Check cache first
    result = await db.execute(
        select(RouteCache).where(
            RouteCache.origin_lat == data.origin_lat,
            RouteCache.origin_lng == data.origin_lng,
            RouteCache.destination_lat == data.destination_lat,
            RouteCache.destination_lng == data.destination_lng,
            RouteCache.transport_mode == data.transport_mode
        )
    )
    cached = result.scalar_one_or_none()
    
    if cached:
        return cached.route_data
    
    # Calculate distance using Haversine formula
    distance = calculate_distance(
        data.origin_lat, data.origin_lng,
        data.destination_lat, data.destination_lng
    )
    
    # Estimate duration based on transport mode
    speed_map = {
        "driving": 60,  # km/h
        "walking": 5,   # km/h
        "transit": 40   # km/h
    }
    speed = speed_map.get(data.transport_mode, 60)
    duration = int((distance / speed) * 60)  # minutes
    
    route_data = {
        "distance": round(distance, 2),
        "duration": duration,
        "transport_mode": data.transport_mode,
        "route_geometry": {
            "type": "LineString",
            "coordinates": [
                [data.origin_lng, data.origin_lat],
                [data.destination_lng, data.destination_lat]
            ]
        }
    }
    
    # Cache the result
    cache_entry = RouteCache(
        origin_lat=data.origin_lat,
        origin_lng=data.origin_lng,
        destination_lat=data.destination_lat,
        destination_lng=data.destination_lng,
        transport_mode=data.transport_mode,
        route_data=route_data
    )
    db.add(cache_entry)
    await db.commit()
    
    return route_data


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula."""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c
