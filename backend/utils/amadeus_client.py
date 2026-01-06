"""
Amadeus API Client for Flight and Hotel Search
Documentation: https://developers.amadeus.com/
"""
import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from src.config import settings


class AmadeusClient:
    """
    Client for Amadeus API integration
    Handles authentication and API calls for flights and hotels
    """
    
    def __init__(self):
        self.api_key = settings.AMADEUS_API_KEY
        self.api_secret = settings.AMADEUS_API_SECRET
        self.base_url = settings.AMADEUS_BASE_URL
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
    async def get_access_token(self) -> str:
        """
        Get or refresh OAuth2 access token
        Tokens are valid for 30 minutes
        """
        # Return cached token if still valid
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at - timedelta(minutes=5):
                return self.access_token
        
        # Request new token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/security/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.api_key,
                    "client_secret": self.api_secret
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get Amadeus access token: {response.text}")
            
            data = response.json()
            self.access_token = data["access_token"]
            expires_in = data.get("expires_in", 1800)  # Default 30 minutes
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            return self.access_token
    
    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Amadeus API"""
        token = await self.get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=f"{self.base_url}{endpoint}",
                params=params,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Amadeus API error ({response.status_code}): {response.text}"
                print(error_msg)
                return {"data": [], "error": error_msg}
    
    # ==================== FLIGHT SEARCH ====================
    
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,  # YYYY-MM-DD format
        adults: int = 1,
        return_date: Optional[str] = None,
        travel_class: str = "ECONOMY",
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for flight offers
        
        Args:
            origin: IATA airport code (e.g., "CGK" for Jakarta)
            destination: IATA airport code (e.g., "DPS" for Bali)
            departure_date: Departure date in YYYY-MM-DD format
            adults: Number of adult passengers
            return_date: Return date for round trip
            travel_class: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
            max_results: Maximum number of results
        """
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "travelClass": travel_class,
            "max": max_results,
            "currencyCode": "IDR"
        }
        
        if return_date:
            params["returnDate"] = return_date
        
        result = await self._make_request("GET", "/v2/shopping/flight-offers", params)
        return result.get("data", [])
    
    async def get_flight_inspirations(
        self,
        origin: str,
        max_price: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get flight inspiration - cheapest destinations from origin
        Useful for budget travelers
        """
        params = {
            "origin": origin,
            "oneWay": "false"
        }
        
        if max_price:
            params["maxPrice"] = max_price
        
        result = await self._make_request("GET", "/v1/shopping/flight-destinations", params)
        return result.get("data", [])
    
    # ==================== HOTEL SEARCH ====================
    
    async def search_hotels_by_city(
        self,
        city_code: str,  # IATA city code (e.g., "DPS" for Denpasar)
        check_in_date: str,  # YYYY-MM-DD
        check_out_date: str,  # YYYY-MM-DD
        adults: int = 1,
        radius: int = 50,  # km
        radius_unit: str = "KM",
        ratings: Optional[List[int]] = None,  # [3, 4, 5]
        amenities: Optional[List[str]] = None,
        price_range: Optional[str] = None,  # e.g., "50-200"
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search hotels by city code
        
        Returns list of hotels with:
        - Hotel ID
        - Name
        - Location (lat/lon)
        - Rating
        - Price estimates (if available)
        """
        params = {
            "cityCode": city_code,
            "radius": radius,
            "radiusUnit": radius_unit,
            "hotelSource": "ALL"
        }
        
        if ratings:
            params["ratings"] = ",".join(map(str, ratings))
        
        if amenities:
            params["amenities"] = ",".join(amenities)
        
        result = await self._make_request("GET", "/v1/reference-data/locations/hotels/by-city", params)
        hotels = result.get("data", [])
        
        # If we have hotels, get their offers (prices)
        if hotels:
            hotel_ids = [h.get("hotelId") for h in hotels[:max_results] if h.get("hotelId")]
            if hotel_ids:
                offers = await self.get_hotel_offers(
                    hotel_ids=hotel_ids,
                    check_in_date=check_in_date,
                    check_out_date=check_out_date,
                    adults=adults
                )
                
                # Merge offers with hotel data
                offers_by_hotel = {o.get("hotel", {}).get("hotelId"): o for o in offers}
                for hotel in hotels:
                    hotel_id = hotel.get("hotelId")
                    if hotel_id in offers_by_hotel:
                        hotel["offer"] = offers_by_hotel[hotel_id]
        
        return hotels[:max_results]
    
    async def search_hotels_by_geocode(
        self,
        latitude: float,
        longitude: float,
        radius: int = 20,  # km
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search hotels by geographic coordinates
        Useful when you have a specific location
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
            "radiusUnit": "KM",
            "hotelSource": "ALL"
        }
        
        result = await self._make_request("GET", "/v1/reference-data/locations/hotels/by-geocode", params)
        return result.get("data", [])[:max_results]
    
    async def get_hotel_offers(
        self,
        hotel_ids: List[str],
        check_in_date: str,
        check_out_date: str,
        adults: int = 1,
        room_quantity: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get hotel offers with pricing for specific hotels
        
        Args:
            hotel_ids: List of Amadeus hotel IDs (max 200)
            check_in_date: YYYY-MM-DD
            check_out_date: YYYY-MM-DD
            adults: Number of adults
            room_quantity: Number of rooms
        """
        params = {
            "hotelIds": ",".join(hotel_ids[:200]),  # API limit
            "checkInDate": check_in_date,
            "checkOutDate": check_out_date,
            "adults": adults,
            "roomQuantity": room_quantity,
            "currency": "IDR",
            "bestRateOnly": "true"
        }
        
        result = await self._make_request("GET", "/v3/shopping/hotel-offers", params)
        return result.get("data", [])
    
    async def get_hotel_by_id(self, hotel_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific hotel"""
        params = {"hotelIds": hotel_id}
        result = await self._make_request("GET", "/v1/reference-data/locations/hotels/by-hotels", params)
        hotels = result.get("data", [])
        return hotels[0] if hotels else None
    
    # ==================== POINTS OF INTEREST ====================
    
    async def get_points_of_interest(
        self,
        latitude: float,
        longitude: float,
        radius: int = 10,
        categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get points of interest (attractions, restaurants, etc.)
        
        Categories: SIGHTS, BEACH_PARK, HISTORICAL, NIGHTLIFE, RESTAURANT, SHOPPING
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius
        }
        
        if categories:
            params["categories"] = ",".join(categories)
        
        result = await self._make_request("GET", "/v1/shopping/activities", params)
        return result.get("data", [])
    
    # ==================== LOCATION UTILITIES ====================
    
    async def search_airport(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search for airports by city name or airport code
        Returns IATA codes needed for flight search
        """
        params = {
            "keyword": keyword,
            "subType": "AIRPORT"
        }
        result = await self._make_request("GET", "/v1/reference-data/locations", params)
        return result.get("data", [])
    
    async def search_city(self, keyword: str) -> List[Dict[str, Any]]:
        """Search for cities - returns city codes for hotel search"""
        params = {
            "keyword": keyword,
            "subType": "CITY"
        }
        result = await self._make_request("GET", "/v1/reference-data/locations", params)
        return result.get("data", [])


# Singleton instance
_amadeus_client: Optional[AmadeusClient] = None

def get_amadeus_client() -> AmadeusClient:
    """Get or create Amadeus client singleton"""
    global _amadeus_client
    if _amadeus_client is None:
        _amadeus_client = AmadeusClient()
    return _amadeus_client
