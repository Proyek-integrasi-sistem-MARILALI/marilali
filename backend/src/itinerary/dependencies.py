"""
Module: services.itinerary.dependencies
Deskripsi:
Reusable dependencies untuk itinerary validation.
Implements dependency chaining untuk validate ownership dan access.
"""

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
    """
    Validate itinerary exists.
    
    Reusable dependency untuk memastikan itinerary_id valid.
    
    Args:
        itinerary_id: ID itinerary yang akan divalidasi
        db: Database session
        
    Returns:
        Itinerary object dari database
        
    Raises:
        HTTPException: Jika itinerary tidak ditemukan
    """
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
    """
    Validate itinerary ownership.
    
    Dependency chaining: valid_itinerary_id + get_current_user -> valid_owned_itinerary
    
    Args:
        itinerary: Itinerary object dari valid_itinerary_id dependency
        current_user: User object dari get_current_user dependency
        
    Returns:
        Itinerary object yang owned oleh current user
        
    Raises:
        HTTPException: Jika user bukan owner itinerary
    """
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
    """
    Validate itinerary is either public or owned by current user.
    
    Dependency chaining untuk public itinerary access.
    
    Args:
        itinerary: Itinerary object dari valid_itinerary_id dependency
        current_user: User object dari get_current_user dependency
        
    Returns:
        Itinerary object yang public atau owned oleh current user
        
    Raises:
        HTTPException: Jika itinerary private dan bukan milik user
    """
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
