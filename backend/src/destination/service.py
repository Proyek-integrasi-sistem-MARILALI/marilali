
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from fastapi import HTTPException

from src.destination.models import Destination
from src.review.models import Review


async def get_destinations(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    country: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
) -> List[Destination]:
    query = select(Destination)
    
    # Apply filters
    if country:
        query = query.where(Destination.country == country)
    
    if category:
        query = query.where(Destination.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Destination.name.ilike(search_term),
                Destination.description.ilike(search_term)
            )
        )
    
    # Order by rating and pagination
    query = query.order_by(Destination.rating.desc().nullslast())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_destination_by_id(
    destination_id: int,
    db: AsyncSession
) -> Destination:
    result = await db.execute(
        select(Destination)
        .options(selectinload(Destination.reviews))
        .where(Destination.id == destination_id)
    )
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    return destination


async def get_popular_destinations(
    db: AsyncSession,
    limit: int = 10
) -> List[Destination]:
    result = await db.execute(
        select(Destination)
        .where(Destination.rating.isnot(None))
        .order_by(
            Destination.rating.desc()
        )
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_destinations_by_country(
    country: str,
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Destination]:
    result = await db.execute(
        select(Destination)
        .where(Destination.country == country)
        .order_by(Destination.name)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def search_destinations(
    search_query: str,
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Destination]:
    search_term = f"%{search_query}%"
    
    result = await db.execute(
        select(Destination)
        .where(
            or_(
                Destination.name.ilike(search_term),
                Destination.description.ilike(search_term),
                Destination.country.ilike(search_term),
                Destination.city.ilike(search_term)
            )
        )
        .order_by(Destination.rating.desc().nullslast())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_destination_reviews(
    destination_id: int,
    db: AsyncSession
) -> List[Review]:
    # Verify destination exists
    await get_destination_by_id(destination_id, db)
    
    result = await db.execute(
        select(Review)
        .where(Review.destination_id == destination_id)
        .order_by(Review.created_at.desc())
    )
    return list(result.scalars().all())
