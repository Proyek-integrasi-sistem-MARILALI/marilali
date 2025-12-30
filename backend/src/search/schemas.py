from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class SearchLogRequest(BaseModel):
    search_type: str = Field(..., description="destination, itinerary, activity")
    query: str
    filters: Optional[Dict] = None
    results_count: int = Field(..., ge=0)


class SearchHistoryResponse(BaseModel):
    id: int
    search_type: str
    query: str
    filters: Optional[Dict]
    results_count: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class PopularSearchResponse(BaseModel):
    query: str
    search_count: int
    last_searched: datetime
    
    class Config:
        from_attributes = True


class TrendingSearchResponse(BaseModel):
    query: str
    count: int
    period_days: int


class SearchAnalyticsResponse(BaseModel):
    period_days: int
    total_searches: int
    by_type: Dict[str, int]
    avg_results_per_search: float
    common_filters: Dict[str, int]


class SearchSuggestionRequest(BaseModel):
    query: str
    search_type: str = Field(..., description="destination, itinerary, activity")
    limit: int = Field(5, ge=1, le=10)


class SearchSuggestionResponse(BaseModel):
    query: str
    suggestions: List[str]
