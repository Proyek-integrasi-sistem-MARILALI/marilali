from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from services.planner.schemas import PlannerInput, PlannerRecommendationResponse
from services.planner import controller

router = APIRouter()

@router.post("/recommendations", response_model=PlannerRecommendationResponse)
def get_recommendations(data: PlannerInput, db: Session = Depends(get_db)):
    result = controller.get_planner_recommendations(data, db)
    return {"recommendations": result}
