from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from sqlalchemy.orm import selectinload
from typing import List

from src.activity.models import Activity
from src.itinerary.models import Itinerary
from src.destination.models import Destination
from src.activity.schemas import ActivityCreate, ActivityUpdate, ActivityBulkReorder
from src.activity.exceptions import (
    ActivityNotFoundException,
    NotActivityOwnerException,
    InvalidDateRangeException,
    ActivityDateOutOfRangeException,
    CannotModifyCompletedActivityException
)


async def verify_itinerary_ownership(itinerary_id: int, user_id: int, db: AsyncSession) -> Itinerary:
    result = await db.execute(
        select(Itinerary).where(Itinerary.id == itinerary_id)
    )
    itinerary = result.scalar_one_or_none()
    
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    if itinerary.user_id != user_id:
        raise NotActivityOwnerException()
    
    return itinerary


async def create_activity(
    itinerary_id: int,
    user_id: int,
    activity_data: ActivityCreate,
    db: AsyncSession
) -> Activity:
    """
    Create new activity in itinerary.
    
    Args:
        itinerary_id: ID of itinerary
        user_id: ID of current user
        activity_data: Activity creation data
        db: Async database session
        
    Returns:
        Created activity
        
    Raises:
        NotActivityOwnerException: If user doesn't own the itinerary
        ActivityDateOutOfRangeException: If activity date is outside itinerary range
        InvalidDateRangeException: If start_time > end_time
    """
    # Verify ownership and get itinerary
    itinerary = await verify_itinerary_ownership(itinerary_id, user_id, db)
    
    # Check if itinerary is completed
    if itinerary.status == "completed":
        raise CannotModifyCompletedActivityException()
    
    # Validate activity date is within itinerary range
    if not (itinerary.start_date <= activity_data.activity_date <= itinerary.end_date):
        raise ActivityDateOutOfRangeException()
    
    # Validate time range
    if activity_data.start_time and activity_data.end_time:
        if activity_data.start_time >= activity_data.end_time:
            raise InvalidDateRangeException("Start time must be before end time")
    
    # Create activity
    activity = Activity(
        itinerary_id=itinerary_id,
        destination_id=activity_data.destination_id,
        title=activity_data.title,
        description=activity_data.description,
        activity_date=activity_data.activity_date,
        start_time=activity_data.start_time,
        end_time=activity_data.end_time,
        location=activity_data.location,
        estimated_cost=activity_data.estimated_cost,
        notes=activity_data.notes,
        order_index=activity_data.order_index
    )
    
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    
    return activity


async def get_itinerary_activities(
    itinerary_id: int,
    user_id: int,
    db: AsyncSession
) -> List[Activity]:
    """
    Get all activities for an itinerary, ordered by order_index and date.
    
    Args:
        itinerary_id: ID of itinerary
        user_id: ID of current user
        db: Async database session
        
    Returns:
        List of activities with destination details
    """
    # Verify ownership
    await verify_itinerary_ownership(itinerary_id, user_id, db)
    
    # Get activities with destination relationship loaded
    result = await db.execute(
        select(Activity)
        .options(selectinload(Activity.destination))
        .where(Activity.itinerary_id == itinerary_id)
        .order_by(Activity.activity_date, Activity.order_index, Activity.start_time)
    )
    
    activities = result.scalars().all()
    return list(activities)


async def get_activity_by_id(
    activity_id: int,
    user_id: int,
    db: AsyncSession
) -> Activity:
    """
    Get specific activity by ID.
    
    Args:
        activity_id: ID of activity
        user_id: ID of current user
        db: Async database session
        
    Returns:
        Activity with destination details
        
    Raises:
        ActivityNotFoundException: If activity not found
        NotActivityOwnerException: If user doesn't own the activity's itinerary
    """
    result = await db.execute(
        select(Activity)
        .options(selectinload(Activity.destination), selectinload(Activity.itinerary))
        .where(Activity.id == activity_id)
    )
    
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise ActivityNotFoundException(activity_id)
    
    if activity.itinerary.user_id != user_id:
        raise NotActivityOwnerException()
    
    return activity


async def update_activity(
    activity_id: int,
    user_id: int,
    activity_data: ActivityUpdate,
    db: AsyncSession
) -> Activity:
    """
    Update existing activity.
    
    Args:
        activity_id: ID of activity
        user_id: ID of current user
        activity_data: Activity update data
        db: Async database session
        
    Returns:
        Updated activity
    """
    # Get activity and verify ownership
    activity = await get_activity_by_id(activity_id, user_id, db)
    
    # Check if itinerary is completed
    if activity.itinerary.status == "completed":
        raise CannotModifyCompletedActivityException()
    
    # Update fields
    update_data = activity_data.model_dump(exclude_unset=True)
    
    # Validate date if provided
    if "activity_date" in update_data:
        itinerary = activity.itinerary
        if not (itinerary.start_date <= update_data["activity_date"] <= itinerary.end_date):
            raise ActivityDateOutOfRangeException()
    
    # Validate time range if both provided
    start_time = update_data.get("start_time", activity.start_time)
    end_time = update_data.get("end_time", activity.end_time)
    if start_time and end_time and start_time >= end_time:
        raise InvalidDateRangeException("Start time must be before end time")
    
    for field, value in update_data.items():
        setattr(activity, field, value)
    
    await db.commit()
    await db.refresh(activity)
    
    return activity


async def delete_activity(
    activity_id: int,
    user_id: int,
    db: AsyncSession
) -> dict:
    """
    Delete activity.
    
    Args:
        activity_id: ID of activity
        user_id: ID of current user
        db: Async database session
        
    Returns:
        Success message
    """
    activity = await get_activity_by_id(activity_id, user_id, db)
    
    # Check if itinerary is completed
    if activity.itinerary.status == "completed":
        raise CannotModifyCompletedActivityException()
    
    await db.delete(activity)
    await db.commit()
    
    return {"message": "Activity deleted successfully"}


async def reorder_activities(
    itinerary_id: int,
    user_id: int,
    reorder_data: ActivityBulkReorder,
    db: AsyncSession
) -> List[Activity]:
    """
    Bulk reorder activities in an itinerary.
    
    Args:
        itinerary_id: ID of itinerary
        user_id: ID of current user
        reorder_data: Bulk reorder data
        db: Async database session
        
    Returns:
        List of reordered activities
    """
    # Verify ownership
    itinerary = await verify_itinerary_ownership(itinerary_id, user_id, db)
    
    # Check if itinerary is completed
    if itinerary.status == "completed":
        raise CannotModifyCompletedActivityException()
    
    # Update order_index for each activity
    for item in reorder_data.activities:
        await db.execute(
            update(Activity)
            .where(
                and_(
                    Activity.id == item.activity_id,
                    Activity.itinerary_id == itinerary_id
                )
            )
            .values(order_index=item.new_order_index)
        )
    
    await db.commit()
    
    # Return updated activities
    return await get_itinerary_activities(itinerary_id, user_id, db)


async def mark_activity_complete(
    activity_id: int,
    user_id: int,
    completed: bool,
    db: AsyncSession
) -> Activity:
    """
    Mark activity as completed or uncompleted.
    
    Args:
        activity_id: ID of activity
        user_id: ID of current user
        completed: Whether to mark as completed
        db: Async database session
        
    Returns:
        Updated activity
    """
    activity = await get_activity_by_id(activity_id, user_id, db)
    
    activity.is_completed = completed
    await db.commit()
    await db.refresh(activity)
    
    return activity
