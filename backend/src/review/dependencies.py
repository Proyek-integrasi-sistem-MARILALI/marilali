"""
Review service dependencies for FastAPI dependency injection.
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db

# Add review-specific dependencies here
