from pydantic import BaseModel, Field
from datetime import datetime

class DestinationBase(BaseModel):
    name: str
    category: str
    location: str
    price: int | None = Field(None, description="Price in Indonesian Rupiah (IDR)")
    description: str | None = None
    image_url: str | None = None

class DestinationCreate(DestinationBase):
    pass

class DestinationUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    location: str | None = None
    price: int | None = Field(None, description="Price in Indonesian Rupiah (IDR)")
    description: str | None = None
    image_url: str | None = None

class DestinationResponse(DestinationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
