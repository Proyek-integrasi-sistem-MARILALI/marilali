from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException

from src.favorite.models import FavoriteDestination, FavoriteItinerary
from src.destination.models import Destination
from src.itinerary.models import Itinerary


async def add_favorite_destination(
    user_id: int,
    destination_id: int,
    notes: Optional[str],
    db: AsyncSession
) -> FavoriteDestination:
    # Check if destination exists
    dest_result = await db.execute(
        select(Destination).where(Destination.id == destination_id)
    )
    destination = dest_result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    # Check if already favorited
    existing = await db.execute(
        select(FavoriteDestination).where(
            and_(
                FavoriteDestination.user_id == user_id,
                FavoriteDestination.destination_id == destination_id
            )
        )
    )
    
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Destination already in favorites")
    
    favorite = FavoriteDestination(
        user_id=user_id,
        destination_id=destination_id,
        notes=notes,
        added_at=datetime.utcnow()
    )
    
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    
    return favorite


async def remove_favorite_destination(
    user_id: int,
    destination_id: int,
    db: AsyncSession
):
    result = await db.execute(
        select(FavoriteDestination).where(
            and_(
                FavoriteDestination.user_id == user_id,
                FavoriteDestination.destination_id == destination_id
            )
        )
    )
    
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    await db.delete(favorite)
    await db.commit()
    
    return {"message": "Removed from favorites"}


async def get_favorite_destinations(
    user_id: int,
    db: AsyncSession
) -> List[FavoriteDestination]:
    result = await db.execute(
        select(FavoriteDestination)
        .where(FavoriteDestination.user_id == user_id)
        .order_by(FavoriteDestination.added_at.desc())
    )
    
    favorites = list(result.scalars().all())
    
    # Load destination details
    for fav in favorites:
        dest_result = await db.execute(
            select(Destination).where(Destination.id == fav.destination_id)
        )
        fav.destination = dest_result.scalar_one_or_none()
    
    return favorites


async def update_favorite_notes(
    user_id: int,
    destination_id: int,
    notes: str,
    db: AsyncSession
) -> FavoriteDestination:
    result = await db.execute(
        select(FavoriteDestination).where(
            and_(
                FavoriteDestination.user_id == user_id,
                FavoriteDestination.destination_id == destination_id
            )
        )
    )
    
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    favorite.notes = notes
    await db.commit()
    await db.refresh(favorite)
    
    return favorite


async def check_is_favorite_destination(
    user_id: int,
    destination_id: int,
    db: AsyncSession
) -> bool:
    result = await db.execute(
        select(FavoriteDestination).where(
            and_(
                FavoriteDestination.user_id == user_id,
                FavoriteDestination.destination_id == destination_id
            )
        )
    )
    
    return result.scalar_one_or_none() is not None


# Itinerary favorites
async def add_favorite_itinerary(
    user_id: int,
    itinerary_id: int,
    notes: Optional[str],
    db: AsyncSession
) -> FavoriteItinerary:
    # Check if itinerary exists and is accessible
    itin_result = await db.execute(
        select(Itinerary).where(Itinerary.id == itinerary_id)
    )
    itinerary = itin_result.scalar_one_or_none()
    
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    # Check if already favorited
    existing = await db.execute(
        select(FavoriteItinerary).where(
            and_(
                FavoriteItinerary.user_id == user_id,
                FavoriteItinerary.itinerary_id == itinerary_id
            )
        )
    )
    
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Itinerary already in favorites")
    
    favorite = FavoriteItinerary(
        user_id=user_id,
        itinerary_id=itinerary_id,
        notes=notes,
        added_at=datetime.utcnow()
    )
    
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    
    return favorite


async def remove_favorite_itinerary(
    user_id: int,
    itinerary_id: int,
    db: AsyncSession
):
    result = await db.execute(
        select(FavoriteItinerary).where(
            and_(
                FavoriteItinerary.user_id == user_id,
                FavoriteItinerary.itinerary_id == itinerary_id
            )
        )
    )
    
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    await db.delete(favorite)
    await db.commit()
    
    return {"message": "Removed from favorites"}


async def get_favorite_itineraries(
    user_id: int,
    db: AsyncSession
) -> List[FavoriteItinerary]:
    result = await db.execute(
        select(FavoriteItinerary)
        .where(FavoriteItinerary.user_id == user_id)
        .order_by(FavoriteItinerary.added_at.desc())
    )
    
    favorites = list(result.scalars().all())
    
    # Load itinerary details
    for fav in favorites:
        itin_result = await db.execute(
            select(Itinerary).where(Itinerary.id == fav.itinerary_id)
        )
        fav.itinerary = itin_result.scalar_one_or_none()
    
    return favorites


async def get_favorites_count(
    user_id: int,
    db: AsyncSession
) -> dict:
    dest_count = await db.execute(
        select(func.count(FavoriteDestination.id))
        .where(FavoriteDestination.user_id == user_id)
    )
    
    itin_count = await db.execute(
        select(func.count(FavoriteItinerary.id))
        .where(FavoriteItinerary.user_id == user_id)
    )
    
    return {
        "destinations": dest_count.scalar(),
        "itineraries": itin_count.scalar(),
        "total": dest_count.scalar() + itin_count.scalar()
    }
