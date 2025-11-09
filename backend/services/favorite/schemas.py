from pydantic import BaseModel
from datetime import datetime

class FavoriteResponse(BaseModel):
    id: int
    destination_id: int
    created_at: datetime

    class Config:
        orm_mode = True
