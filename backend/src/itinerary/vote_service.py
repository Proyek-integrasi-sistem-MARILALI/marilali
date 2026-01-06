from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError
from src.user.models import User
from src.itinerary.models import Itinerary
from src.itinerary.vote_models import ItineraryVote

async def vote_itinerary(
    user_id: int,
    itinerary_id: int,
    vote_type: str,  # 'upvote' or 'downvote'
    db: AsyncSession
):
    """
    Vote on an itinerary (upvote or downvote).
    Uses dedicated itinerary_votes table.
    """
    # Validate vote_type
    if vote_type not in ['upvote', 'downvote']:
        raise ValueError("Invalid vote_type. Must be 'upvote' or 'downvote'")
    
    # Check if itinerary exists
    result = await db.execute(select(Itinerary).where(Itinerary.id == itinerary_id))
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise ValueError("Itinerary not found")
    
    # Check if user already has a vote
    result = await db.execute(
        select(ItineraryVote).where(
            ItineraryVote.user_id == user_id,
            ItineraryVote.itinerary_id == itinerary_id
        )
    )
    existing_vote = result.scalar_one_or_none()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Same vote type - remove the vote
            await db.delete(existing_vote)
            await db.commit()
            return {"message": f"{vote_type.capitalize()} removed", "vote_type": None}
        else:
            # Different vote type - switch the vote
            existing_vote.vote_type = vote_type
            await db.commit()
            return {"message": f"Switched to {vote_type}", "vote_type": vote_type}
    else:
        # No existing vote - create new one
        new_vote = ItineraryVote(
            user_id=user_id,
            itinerary_id=itinerary_id,
            vote_type=vote_type
        )
        db.add(new_vote)
        try:
            await db.commit()
            return {"message": f"{vote_type.capitalize()}d successfully", "vote_type": vote_type}
        except IntegrityError:
            await db.rollback()
            raise ValueError("Failed to record vote")


async def get_user_vote(
    user_id: int,
    itinerary_id: int,
    db: AsyncSession
):
    """Get user's current vote on an itinerary"""
    result = await db.execute(
        select(ItineraryVote).where(
            ItineraryVote.user_id == user_id,
            ItineraryVote.itinerary_id == itinerary_id
        )
    )
    vote = result.scalar_one_or_none()
    
    if vote:
        return {"vote_type": vote.vote_type}
    
    return {"vote_type": None}


async def get_vote_counts(
    itinerary_id: int,
    db: AsyncSession
):
    """Get upvote and downvote counts for an itinerary"""
    result = await db.execute(
        select(
            func.count().filter(ItineraryVote.vote_type == 'upvote').label('upvotes'),
            func.count().filter(ItineraryVote.vote_type == 'downvote').label('downvotes')
        ).where(ItineraryVote.itinerary_id == itinerary_id)
    )
    counts = result.one()
    
    return {
        "upvotes": counts.upvotes or 0,
        "downvotes": counts.downvotes or 0
    }
