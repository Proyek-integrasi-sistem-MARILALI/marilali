from pydantic import BaseModel
from typing import Optional

class PreferenceBase(BaseModel):
    preferred_category: Optional[str] = None
    min_budget: Optional[int] = None
    max_budget: Optional[int] = None
    weather_preference: Optional[str] = None


class PreferenceResponse(PreferenceBase):
    id: int

    class Config:
        orm_mode = True
