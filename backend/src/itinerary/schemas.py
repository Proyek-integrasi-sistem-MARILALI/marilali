from pydantic import ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from src.schemas import CustomModel


class UserBasicInfo(CustomModel):
    id: Optional[int] = None
    name: Optional[str] = None
    profile_picture: Optional[str] = None


class FlightSchema(CustomModel):
    id: Optional[int] = None
    airline: Optional[str] = None
    departure_city: Optional[str] = None
    arrival_city: Optional[str] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    price: Optional[int] = None


class AccommodationSchema(CustomModel):
    id: Optional[int] = None
    name: Optional[str] = None
    location: Optional[str] = None
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    price_per_night: Optional[int] = None


class ItineraryCreate(CustomModel):
    title: str
    start_date: date
    end_date: date
    budget: Optional[int] = None
    category: Optional[str] = None
    flights: List[FlightSchema] = []
    accommodations: List[AccommodationSchema] = []


class ItineraryUpdate(CustomModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    category: Optional[str] = None


class ItineraryResponse(CustomModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    user_profile_picture: Optional[str] = None
    user: Optional[UserBasicInfo] = None
    title: str
    start_date: date
    end_date: date
    budget: Optional[int] = None
    total_budget: Optional[int] = None
    status: Optional[str] = "planned"
    is_public: bool = False
    created_at: datetime
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    destination_city: Optional[str] = None
    destination_country: Optional[str] = None
    origin_city: Optional[str] = None
    person_count: Optional[int] = None
    notes: Optional[str] = None
    category: Optional[str] = None
    upvotes: Optional[int] = 0
    downvotes: Optional[int] = 0
    flights: List[FlightSchema] = []
    accommodations: List[AccommodationSchema] = []
    
    @staticmethod
    def from_orm(itinerary):
        # Count upvotes and downvotes from dedicated votes table
        upvotes = 0
        downvotes = 0
        
        if hasattr(itinerary, 'votes') and itinerary.votes:
            for vote in itinerary.votes:
                if vote.vote_type == 'upvote':
                    upvotes += 1
                elif vote.vote_type == 'downvote':
                    downvotes += 1
        
        data = {
            "id": itinerary.id,
            "user_id": itinerary.user_id,
            "user_name": itinerary.user.name if itinerary.user else None,
            "user_profile_picture": itinerary.user.profile_picture if itinerary.user else None,
            "user": UserBasicInfo(
                id=itinerary.user.id if itinerary.user else None,
                name=itinerary.user.name if itinerary.user else None,
                profile_picture=itinerary.user.profile_picture if itinerary.user else None
            ) if itinerary.user else None,
            "title": itinerary.title,
            "start_date": itinerary.start_date,
            "end_date": itinerary.end_date,
            "budget": itinerary.budget,
            "total_budget": itinerary.budget,
            "status": itinerary.status,
            "is_public": itinerary.is_public,
            "created_at": itinerary.created_at,
            "image_url": itinerary.thumbnail_url,
            "thumbnail_url": itinerary.thumbnail_url,
            "destination_city": itinerary.destination_city,
            "destination_country": itinerary.destination_country,
            "origin_city": getattr(itinerary, 'origin_city', None),
            "person_count": getattr(itinerary, 'person_count', 1),
            "notes": getattr(itinerary, 'notes', None),
            "category": getattr(itinerary, 'category', None),
            "upvotes": upvotes,
            "downvotes": downvotes,
            "flights": [FlightSchema(**f.__dict__) for f in itinerary.flights] if itinerary.flights else [],
            "accommodations": [AccommodationSchema(**a.__dict__) for a in itinerary.accommodations] if itinerary.accommodations else [],
        }
        return ItineraryResponse(**data)


class ItineraryShareResponse(CustomModel):
    id: int
    is_public: bool
