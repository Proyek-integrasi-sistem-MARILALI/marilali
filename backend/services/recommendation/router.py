from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.recommendation.schemas import RecommendationRequest, RecommendationResponse
from services.recommendation.controller import generate_recommendations
from database.connection import get_db

router = APIRouter()

@router.post("/", response_model=RecommendationResponse)
def get_recommendations(data: RecommendationRequest, db: Session = Depends(get_db)):
    return generate_recommendations(data, db)
