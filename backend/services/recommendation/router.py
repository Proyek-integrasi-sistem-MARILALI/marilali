from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.recommendation.controller import recommend_destinations_by_budget
from services.recommendation.schemas import RecommendationDestinationResponse
from database.connection import get_db

router = APIRouter()

@router.get("/by-budget", response_model=list[RecommendationDestinationResponse])
def rekomendasi_budget(
    budget: int,
    sort: str = "cheapest",
    db: Session = Depends(get_db)
):
    return recommend_destinations_by_budget(db, budget, sort)
