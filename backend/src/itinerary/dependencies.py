from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.itinerary.models import Itinerary
from src.user.models import User
from src.auth.dependencies import get_current_user


async def valid_itinerary_id(
    itinerary_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Itinerary:
    result = await db.execute(
        select(Itinerary).where(Itinerary.id == itinerary_id)
    )
    itinerary = result.scalar_one_or_none()
    
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )
    
    return itinerary


async def valid_owned_itinerary(
    itinerary: Annotated[Itinerary, Depends(valid_itinerary_id)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> Itinerary:
    if itinerary.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this itinerary"
        )
    
    return itinerary


async def valid_public_or_owned_itinerary(
    itinerary: Annotated[Itinerary, Depends(valid_itinerary_id)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> Itinerary:
    if not itinerary.is_public and itinerary.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This itinerary is private"
        )
    
    return itinerary


# Type aliases untuk cleaner route signatures
ValidItinerary = Annotated[Itinerary, Depends(valid_itinerary_id)]
OwnedItinerary = Annotated[Itinerary, Depends(valid_owned_itinerary)]
AccessibleItinerary = Annotated[Itinerary, Depends(valid_public_or_owned_itinerary)]
