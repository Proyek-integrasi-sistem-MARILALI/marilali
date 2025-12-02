from pydantic import BaseModel

class ItinerarySummaryResponse(BaseModel):
    itinerary_id: int
    title: str
    total_flight: int
    total_accommodation: int
    total_activity: int
    grand_total: int

    class Config:
        orm_mode = True
