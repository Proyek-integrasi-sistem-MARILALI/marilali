"""
Map schemas for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LocationCreate(BaseModel):
    """Schema for creating a saved location."""
    name: str
    address: Optional[str] = None
    latitude: float
    longitude: float
    place_type: Optional[str] = None
    notes: Optional[str] = None


class LocationResponse(BaseModel):
    """Schema for location response."""
    id: int
    user_id: int
    name: str
    address: Optional[str]
    latitude: float
    longitude: float
    place_type: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class RouteRequest(BaseModel):
    """Schema for route calculation request."""
    origin_lat: float
    origin_lng: float
    destination_lat: float
    destination_lng: float
    transport_mode: str = Field(default="driving", description="driving, walking, or transit")


class RouteResponse(BaseModel):
    """Schema for route response."""
    distance: float = Field(description="Distance in kilometers")
    duration: int = Field(description="Duration in minutes")
    route_geometry: dict = Field(description="Route coordinates and geometry")
    transport_mode: str
    
    model_config = {"from_attributes": True}


class NearbySearchRequest(BaseModel):
    """Schema for nearby places search."""
    latitude: float
    longitude: float
    radius: int = Field(default=5000, description="Search radius in meters")
    place_type: Optional[str] = Field(default=None, description="restaurant, hotel, attraction, etc.")
    max_results: int = Field(default=20, le=50)
