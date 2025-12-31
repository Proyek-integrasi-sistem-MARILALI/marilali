"""
Module: services.itinerary.controller
Deskripsi:
Async business logic untuk manajemen itinerary perjalanan.
"""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.itinerary.models import Itinerary, Flight, Accommodation, Transportation


async def create_itinerary(user_id: int, data, db: AsyncSession):
    """Create new itinerary for user."""
    new_itinerary = Itinerary(
        user_id=user_id,
        title=data.title,
        start_date=data.start_date,
        end_date=data.end_date,
        budget=data.budget
    )
    db.add(new_itinerary)
    await db.commit()
    await db.refresh(new_itinerary)
    return new_itinerary


async def get_all_itineraries(user_id: int, db: AsyncSession):
    """Get all itineraries for a user."""
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.user_id == user_id)
        .options(
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations)
        )
    )
    return result.scalars().all()


async def get_itinerary_by_id(itinerary_id: int, user_id: int, db: AsyncSession):
    """Get specific itinerary by ID."""
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id, Itinerary.user_id == user_id)
        .options(
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations)
        )
    )
    itinerary = result.scalar_one_or_none()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return itinerary


async def delete_itinerary(itinerary_id: int, user_id: int, db: AsyncSession):
    """Delete itinerary."""
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id, Itinerary.user_id == user_id)
    )
    itinerary = result.scalar_one_or_none()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    await db.delete(itinerary)
    await db.commit()
    return {"message": "Itinerary deleted successfully"}


async def get_completed_itineraries(user_id: int, db: AsyncSession):
    """Get all completed itineraries."""
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.user_id == user_id, Itinerary.status == "completed")
        .options(
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations)
        )
    )
    return result.scalars().all()


async def mark_itinerary_complete(itinerary_id: int, user_id: int, db: AsyncSession):
    """Mark itinerary as completed."""
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id, Itinerary.user_id == user_id)
    )
    itinerary = result.scalar_one_or_none()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    itinerary.status = "completed"
    await db.commit()
    await db.refresh(itinerary)

    return {"message": "Itinerary marked as completed", "status": itinerary.status}


async def copy_itinerary(itinerary_id: int, user_id: int, db: AsyncSession):
    """Copy itinerary with all flights and accommodations."""
    # Get original itinerary
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id, Itinerary.user_id == user_id)
        .options(
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations)
        )
    )
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    # Create new itinerary
    new_itinerary = Itinerary(
        user_id=user_id,
        title=original.title + " (Copy)",
        start_date=original.start_date,
        end_date=original.end_date,
        budget=original.budget,
        status="planned",
    )
    db.add(new_itinerary)
    await db.commit()
    await db.refresh(new_itinerary)

    # Copy flights
    for f in original.flights:
        new_flight = Flight(
            itinerary_id=new_itinerary.id,
            airline=f.airline,
            departure_city=f.departure_city,
            arrival_city=f.arrival_city,
            departure_time=f.departure_time,
            arrival_time=f.arrival_time,
            price=f.price,
        )
        db.add(new_flight)

    # Copy accommodations
    for a in original.accommodations:
        new_accommodation = Accommodation(
            itinerary_id=new_itinerary.id,
            name=a.name,
            location=a.location,
            check_in=a.check_in,
            check_out=a.check_out,
            price_per_night=a.price_per_night,
        )
        db.add(new_accommodation)

    await db.commit()
    await db.refresh(new_itinerary)
    return new_itinerary


async def share_itinerary(itinerary_id: int, user_id: int, db: AsyncSession):
    """Share itinerary by making it public."""
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id, Itinerary.user_id == user_id)
    )
    itinerary = result.scalar_one_or_none()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    itinerary.is_public = True
    await db.commit()
    await db.refresh(itinerary)

    return itinerary


async def get_public_itineraries(db: AsyncSession):
    """Get all public itineraries."""
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.is_public == True)
        .options(
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations)
        )
    )
    return result.scalars().all()


async def copy_itinerary(itinerary_id: int, user_id: int, db: AsyncSession):
    """
    Menyalin itinerary beserta flights & accommodations.
    """
    # Cek itinerary asli
    result = await db.execute(
        select(Itinerary).where(
            Itinerary.id == itinerary_id,
            Itinerary.user_id == user_id
        )
    )
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")

    # Buat itinerary baru
    new_itinerary = Itinerary(
        user_id=user_id,
        title=original.title + " (Copy)",
        start_date=original.start_date,
        end_date=original.end_date,
        budget=original.budget,
        status="planned",
    )
    db.add(new_itinerary)
    await db.commit()
    await db.refresh(new_itinerary)

    # Copy Flights
    result = await db.execute(
        select(Flight).where(Flight.itinerary_id == itinerary_id)
    )
    original_flights = result.scalars().all()
    
    for f in original_flights:
        new_flight = Flight(
            itinerary_id=new_itinerary.id,
            airline=f.airline,
            departure_city=f.departure_city,
            arrival_city=f.arrival_city,
            departure_time=f.departure_time,
            arrival_time=f.arrival_time,
            price=f.price,
        )
        db.add(new_flight)

    # Copy Accommodations
    result = await db.execute(
        select(Accommodation).where(Accommodation.itinerary_id == itinerary_id)
    )
    original_accommodations = result.scalars().all()
    
    for a in original_accommodations:
        new_accommodation = Accommodation(
            itinerary_id=new_itinerary.id,
            name=a.name,
            location=a.location,
            check_in=a.check_in,
            check_out=a.check_out,
            price_per_night=a.price_per_night,
        )
        db.add(new_accommodation)

    await db.commit()
    await db.refresh(new_itinerary)
    return new_itinerary


async def share_itinerary(itinerary_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Itinerary).where(
            Itinerary.id == itinerary_id,
            Itinerary.user_id == user_id
        )
    )
    itinerary = result.scalar_one_or_none()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary tidak ditemukan")

    itinerary.is_public = True
    await db.commit()
    await db.refresh(itinerary)

    return itinerary


async def get_public_itineraries(db: AsyncSession):
    result = await db.execute(
        select(Itinerary).where(Itinerary.is_public == True)
    )
    return result.scalars().all()
