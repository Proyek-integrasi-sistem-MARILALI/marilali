from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.itinerary.models import Itinerary, Flight, Accommodation, Transportation
from src.activity.models import Activity
from src.itinerary.schemas import ItineraryResponse


async def create_itinerary(user_id: int, data, db: AsyncSession):
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
    
    # Load relationships eagerly to prevent MissingGreenlet error in response serialization
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.id == new_itinerary.id)
        .options(
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations)
        )
    )
    return result.scalar_one()


async def get_all_itineraries(user_id: int, db: AsyncSession, skip: int = 0, limit: int = 50):
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.user_id == user_id, Itinerary.status != "completed")
        .options(
            selectinload(Itinerary.user),
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations),
            selectinload(Itinerary.favorite_itineraries),
            selectinload(Itinerary.votes)  # Eager load votes to prevent N+1
        )
        .offset(skip)
        .limit(limit)
    )
    itineraries = result.scalars().all()
    # Convert to ItineraryResponse to properly count votes and format fields
    return [ItineraryResponse.from_orm(itin) for itin in itineraries]


async def get_itinerary_by_id(itinerary_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id, Itinerary.user_id == user_id)
        .options(
            selectinload(Itinerary.user),
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations),
            selectinload(Itinerary.favorite_itineraries),
            selectinload(Itinerary.votes)  # Eager load votes
        )
    )
    itinerary = result.scalar_one_or_none()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    # Convert to ItineraryResponse to properly count votes
    return ItineraryResponse.from_orm(itinerary)


async def update_itinerary(itinerary_id: int, user_id: int, data, db: AsyncSession):
    result = await db.execute(
        select(Itinerary)
        .options(
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations)
        )
        .where(Itinerary.id == itinerary_id, Itinerary.user_id == user_id)
    )
    itinerary = result.scalar_one_or_none()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    # Update only provided fields
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(itinerary, field, value)

    await db.commit()
    await db.refresh(itinerary)
    return itinerary


async def delete_itinerary(itinerary_id: int, user_id: int, db: AsyncSession):
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


async def get_completed_itineraries(user_id: int, db: AsyncSession, skip: int = 0, limit: int = 50):
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.user_id == user_id, Itinerary.status == "completed")
        .options(
            selectinload(Itinerary.user),
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations),
            selectinload(Itinerary.favorite_itineraries),
            selectinload(Itinerary.votes)  # Eager load votes to prevent N+1
        )
        .offset(skip)
        .limit(limit)
    )
    itineraries = result.scalars().all()
    # Convert to ItineraryResponse to properly count votes and format fields
    return [ItineraryResponse.from_orm(itin) for itin in itineraries]

async def mark_itinerary_complete(itinerary_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Itinerary)
        .options(
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations),
            selectinload(Itinerary.activities)
        )
        .where(Itinerary.id == itinerary_id, Itinerary.user_id == user_id)
    )
    itinerary = result.scalar_one_or_none()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    itinerary.status = "completed"
    await db.commit()
    await db.refresh(itinerary)

    return itinerary


async def restore_itinerary(itinerary_id: int, user_id: int, db: AsyncSession):
    # Get original itinerary with all relationships
    result = await db.execute(
        select(Itinerary)
        .options(
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations),
            selectinload(Itinerary.activities)
        )
        .where(Itinerary.id == itinerary_id, Itinerary.user_id == user_id)
    )
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    # Create new itinerary copy with planned status
    new_itinerary = Itinerary(
        user_id=user_id,
        title=original.title,
        start_date=original.start_date,
        end_date=original.end_date,
        budget=original.budget,
        status="planned",
        destination_city=original.destination_city,
        destination_country=original.destination_country,
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

    # Copy activities
    for act in original.activities:
        new_activity = Activity(
            itinerary_id=new_itinerary.id,
            destination_id=act.destination_id,
            title=act.title,
            description=act.description,
            activity_date=act.activity_date,
            start_time=act.start_time,
            end_time=act.end_time,
            location=act.location,
            estimated_cost=act.estimated_cost,
            actual_cost=act.actual_cost,
            order_index=act.order_index,
            notes=act.notes,
            is_completed=False,
        )
        db.add(new_activity)

    await db.commit()
    
    # Reload the new itinerary with all relationships
    result = await db.execute(
        select(Itinerary)
        .options(
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations),
            selectinload(Itinerary.activities)
        )
        .where(Itinerary.id == new_itinerary.id)
    )
    new_itinerary = result.scalar_one()
    return new_itinerary


async def copy_itinerary(itinerary_id: int, user_id: int, db: AsyncSession):
    # Get original itinerary with all relationships
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id, Itinerary.user_id == user_id)
        .options(
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations),
            selectinload(Itinerary.activities)
        )
    )
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    # Create new itinerary
    new_itinerary = Itinerary(
        user_id=user_id,
        title=original.title + " (history)",
        start_date=original.start_date,
        end_date=original.end_date,
        budget=original.budget,
        status="planned",
        destination_city=original.destination_city,
        destination_country=original.destination_country,
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

    # Copy activities
    for act in original.activities:
        new_activity = Activity(
            itinerary_id=new_itinerary.id,
            destination_id=act.destination_id,
            title=act.title,
            description=act.description,
            activity_date=act.activity_date,
            start_time=act.start_time,
            end_time=act.end_time,
            location=act.location,
            estimated_cost=act.estimated_cost,
            actual_cost=act.actual_cost,
            order_index=act.order_index,
            notes=act.notes,
            is_completed=False,
        )
        db.add(new_activity)

    await db.commit()
    
    # Reload the new itinerary with all relationships
    result = await db.execute(
        select(Itinerary)
        .options(
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations),
            selectinload(Itinerary.activities)
        )
        .where(Itinerary.id == new_itinerary.id)
    )
    new_itinerary = result.scalar_one()
    return new_itinerary


async def share_itinerary(itinerary_id: int, user_id: int, db: AsyncSession):
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
    result = await db.execute(
        select(Itinerary)
        .where(Itinerary.is_public == True)
        .options(
            selectinload(Itinerary.user),
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations),
            selectinload(Itinerary.favorite_itineraries)
        )
    )
    return result.scalars().all()





async def share_itinerary(itinerary_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Itinerary)
        .options(
            selectinload(Itinerary.user),
            selectinload(Itinerary.flights),
            selectinload(Itinerary.accommodations)
        )
        .where(
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
