from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.activity import service
from src.activity.schemas import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityBulkReorder
)
from src.auth.security import get_current_user
from src.database import get_db
from src.user.models import User


router = APIRouter()


@router.post("/itinerary/{itinerary_id}/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    itinerary_id: int,
    activity_data: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.create_activity(itinerary_id, current_user.id, activity_data, db)


@router.get("/itinerary/{itinerary_id}/activities", response_model=List[ActivityResponse])
async def get_itinerary_activities(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_itinerary_activities(itinerary_id, current_user.id, db)


@router.get("/activities/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_activity_by_id(activity_id, current_user.id, db)


@router.put("/activities/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    activity_data: ActivityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.update_activity(activity_id, current_user.id, activity_data, db)


@router.delete("/activities/{activity_id}", status_code=status.HTTP_200_OK)
async def delete_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.delete_activity(activity_id, current_user.id, db)


@router.put("/itinerary/{itinerary_id}/activities/reorder", response_model=List[ActivityResponse])
async def reorder_activities(
    itinerary_id: int,
    reorder_data: ActivityBulkReorder,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.reorder_activities(itinerary_id, current_user.id, reorder_data, db)


@router.patch("/activities/{activity_id}/complete", response_model=ActivityResponse)
async def mark_activity_complete(
    activity_id: int,
    completed: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.mark_activity_complete(activity_id, current_user.id, completed, db)
