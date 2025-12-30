from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from src.models import Base


class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    search_type = Column(String(50), nullable=False)  # destination, itinerary, activity
    query = Column(Text, nullable=False)
    filters = Column(JSON, nullable=True)  # Applied filters
    results_count = Column(Integer, nullable=False, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class PopularSearch(Base):
    __tablename__ = "popular_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    search_type = Column(String(50), nullable=False, index=True)
    query = Column(String(255), nullable=False, index=True)
    search_count = Column(Integer, default=1, nullable=False)
    first_searched = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_searched = Column(DateTime, default=datetime.utcnow, nullable=False)
