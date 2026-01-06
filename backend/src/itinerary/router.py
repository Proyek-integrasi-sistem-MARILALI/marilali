from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.itinerary import service, vote_service
from src.itinerary.schemas import ItineraryCreate, ItineraryUpdate, ItineraryResponse
from src.auth.security import get_current_user
from src.database import get_db
from src.user.models import User
from pydantic import BaseModel


router = APIRouter()


class VoteRequest(BaseModel):
    vote_type: str  # 'upvote' or 'downvote'


@router.post("/", response_model=ItineraryResponse)
async def create_itinerary(
    data: ItineraryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.create_itinerary(current_user.id, data, db)


@router.get("/", response_model=list[ItineraryResponse])
async def list_itineraries(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_all_itineraries(current_user.id, db, skip, limit)


@router.get("/history", response_model=list[ItineraryResponse])
async def get_history(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_completed_itineraries(current_user.id, db, skip, limit)


@router.get("/{itinerary_id}", response_model=ItineraryResponse)
async def get_itinerary(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_itinerary_by_id(itinerary_id, current_user.id, db)


@router.put("/{itinerary_id}", response_model=ItineraryResponse)
async def update_itinerary(
    itinerary_id: int,
    data: ItineraryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.update_itinerary(itinerary_id, current_user.id, data, db)


@router.put("/{itinerary_id}/complete", response_model=ItineraryResponse)
async def mark_itinerary_complete(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.mark_itinerary_complete(itinerary_id, current_user.id, db)


@router.put("/{itinerary_id}/restore", response_model=ItineraryResponse)
async def restore_itinerary(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.restore_itinerary(itinerary_id, current_user.id, db)


@router.post("/{itinerary_id}/copy", response_model=ItineraryResponse)
async def copy_itinerary(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.copy_itinerary(itinerary_id, current_user.id, db)


@router.put("/{itinerary_id}/share", response_model=ItineraryResponse)
async def share_itinerary_route(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.share_itinerary(itinerary_id, current_user.id, db)


@router.delete("/{itinerary_id}")
async def delete_itinerary(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.delete_itinerary(itinerary_id, current_user.id, db)


@router.post("/{itinerary_id}/vote")
async def vote_on_itinerary(
    itinerary_id: int,
    vote_request: VoteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Vote on an itinerary (upvote or downvote)"""
    return await vote_service.vote_itinerary(
        user_id=current_user.id,
        itinerary_id=itinerary_id,
        vote_type=vote_request.vote_type,
        db=db
    )


@router.get("/{itinerary_id}/vote")
async def get_user_vote_on_itinerary(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's current vote on an itinerary"""
    return await vote_service.get_user_vote(
        user_id=current_user.id,
        itinerary_id=itinerary_id,
        db=db
    )
