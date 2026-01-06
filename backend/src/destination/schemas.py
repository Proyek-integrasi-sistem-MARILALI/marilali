from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DestinationBase(BaseModel):
    name: str
    category: str
    location: str
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    price: Optional[int] = Field(None, description="Price in Indonesian Rupiah (IDR)")
    rating: Optional[float] = Field(None, description="Average rating")
    description: Optional[str] = None
    image_url: Optional[str] = None
    opening_hours: Optional[str] = None
    contact_info: Optional[str] = None
    website: Optional[str] = None
    source: Optional[str] = "manual"
    osm_id: Optional[str] = None
    osm_type: Optional[str] = None

class DestinationCreate(DestinationBase):
    pass

class DestinationUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    price: Optional[int] = Field(None, description="Price in Indonesian Rupiah (IDR)")
    rating: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    opening_hours: Optional[str] = None
    contact_info: Optional[str] = None
    website: Optional[str] = None

class DestinationResponse(DestinationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
