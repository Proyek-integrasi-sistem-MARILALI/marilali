from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.destination import service
from src.destination.schemas import DestinationResponse
from src.database import get_db


router = APIRouter()


@router.get("/", response_model=List[DestinationResponse])
async def list_destinations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    country: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_destinations(
        db=db,
        skip=skip,
        limit=limit,
        country=country,
        category=category,
        search=search
    )


@router.get("/popular", response_model=List[DestinationResponse])
async def get_popular_destinations(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    return await service.get_popular_destinations(db=db, limit=limit)


@router.get("/search", response_model=List[DestinationResponse])
async def search_destinations(
    q: str = Query(..., min_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    return await service.search_destinations(
        search_query=q,
        db=db,
        skip=skip,
        limit=limit
    )


@router.get("/country/{country}", response_model=List[DestinationResponse])
async def get_destinations_by_country(
    country: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    return await service.get_destinations_by_country(
        country=country,
        db=db,
        skip=skip,
        limit=limit
    )


@router.get("/{destination_id}", response_model=DestinationResponse)
async def get_destination(
    destination_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_destination_by_id(destination_id, db)
