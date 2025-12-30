from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from src.ai_recommendation import service
from src.ai_recommendation.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    FeedbackCreate,
    FeedbackResponse,
    ItinerarySuggestionRequest,
    ItinerarySuggestionResponse
)
from src.auth.security import get_current_user
from src.database import get_db
from src.user.models import User


router = APIRouter()


@router.post("/destinations", response_model=List[RecommendationResponse])
async def get_destination_recommendations(
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered destination recommendations.
    
    **Considers:**
    - Your budget constraints (in IDR - Indonesian Rupiah)
    - Travel dates (for weather)
    - Your preferences and past behavior
    - Destination ratings and popularity
    
    **Budget Optimization:**
    - Filters destinations within your budget
    - Suggests optimal allocation (40% flights, 35% accommodation, 25% activities)
    - Shows budget status and remaining balance
    
    **Use Case:** "Get AI Recommendations"
    """
    travel_dates = None
    if request.start_date and request.end_date:
        travel_dates = {
            "start_date": request.start_date.isoformat(),
            "end_date": request.end_date.isoformat()
        }
    
    recommendations = await service.get_destination_recommendations(
        user_id=current_user.id,
        budget_min=request.budget_min,
        budget_max=request.budget_max,
        travel_dates=travel_dates,
        preferences=request.preferences,
        limit=request.limit or 10,
        db=db
    )
    
    # Format response with budget optimization data
    response_data = []
    for rec in recommendations:
        # Extract data from reasoning JSON field
        reasoning = rec.reasoning if isinstance(rec.reasoning, dict) else {}
        
        rec_dict = {
            "id": rec.id,
            "destination_id": rec.destination_id,
            "recommendation_type": rec.recommendation_type,
            "confidence_score": rec.confidence_score,
            "reasoning": reasoning,
            "created_at": rec.created_at,
            "destination": {
                "id": rec.destination.id,
                "name": rec.destination.name,
                "city": rec.destination.city,
                "category": rec.destination.category,
                "price": float(rec.destination.price) if rec.destination.price else 0,
                "rating": float(rec.destination.rating) if rec.destination.rating else None,
                "description": rec.destination.description,
                "location": rec.destination.location
            } if rec.destination else None
        }
        
        # Note: weather_context is already in reasoning, no need to duplicate it
        
        response_data.append(rec_dict)
    
    return response_data


@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def rate_recommendation(
    feedback: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rate a recommendation to help improve AI accuracy.
    
    **Rating Scale:**
    - 5: Excellent recommendation
    - 4: Good recommendation
    - 3: Okay recommendation
    - 2: Poor recommendation
    - 1: Very poor recommendation
    
    **Use Case:** "Rate Recommendations"
    """
    return await service.rate_recommendation(
        recommendation_id=feedback.recommendation_id,
        user_id=current_user.id,
        rating=feedback.rating,
        feedback_text=feedback.feedback_text,
        db=db
    )


@router.get("/history", response_model=List[RecommendationResponse])
async def get_recommendation_history(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get your recommendation history.
    
    **Use Case:** View past recommendations and revisit suggestions
    """
    return await service.get_user_recommendation_history(
        user_id=current_user.id,
        db=db,
        limit=limit
    )


@router.post("/itinerary/suggestions", response_model=ItinerarySuggestionResponse)
async def get_itinerary_suggestions(
    request: ItinerarySuggestionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered itinerary suggestions for a destination.
    
    **Provides:**
    - Budget allocation suggestions
    - Daily activity recommendations
    - Cost estimates per category
    - Travel tips
    
    **Use Case:** "Generate Auto Itinerary"
    """
    return await service.get_smart_itinerary_suggestions(
        user_id=current_user.id,
        destination_id=request.destination_id,
        days=request.days,
        budget=request.budget,
        db=db
    )
