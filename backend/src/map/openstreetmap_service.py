import httpx
import asyncio
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json

from src.config import settings


class OpenStreetMapService:
    def __init__(self):
        self.nominatim_url = settings.OSM_NOMINATIM_URL
        self.overpass_url = settings.OSM_OVERPASS_URL
        self.user_agent = settings.OSM_USER_AGENT
        self.bali_bbox = (
            settings.BALI_MIN_LAT,
            settings.BALI_MIN_LON,
            settings.BALI_MAX_LAT,
            settings.BALI_MAX_LON
        )
        
    async def search_pois_by_tags(
        self,
        tags: Dict[str, str],
        limit: int = 100
    ) -> List[Dict]:
        # Build Overpass QL query
        tag_filters = "".join([f'["{k}"="{v}"]' for k, v in tags.items()])
        bbox = f"{self.bali_bbox[0]},{self.bali_bbox[1]},{self.bali_bbox[2]},{self.bali_bbox[3]}"
        
        query = f"""
        [out:json][timeout:25];
        (
          node{tag_filters}({bbox});
          way{tag_filters}({bbox});
          relation{tag_filters}({bbox});
        );
        out center {limit};
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.overpass_url,
                    data=query,
                    headers={"User-Agent": self.user_agent},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                pois = []
                for element in data.get("elements", []):
                    poi = self._parse_osm_element(element)
                    if poi:
                        pois.append(poi)
                
                return pois
                
        except httpx.HTTPError as e:
            print(f"OSM API error: {e}")
            return []
    
    async def get_bali_attractions(self) -> List[Dict]:
        return await self.search_pois_by_tags({"tourism": "attraction"})
    
    async def get_bali_hotels(self) -> List[Dict]:
        return await self.search_pois_by_tags({"tourism": "hotel"})
    
    async def get_bali_restaurants(self) -> List[Dict]:
        restaurants = await self.search_pois_by_tags({"amenity": "restaurant"})
        cafes = await self.search_pois_by_tags({"amenity": "cafe"})
        return restaurants + cafes
    
    async def get_bali_beaches(self) -> List[Dict]:
        return await self.search_pois_by_tags({"natural": "beach"})
    
    async def get_bali_temples(self) -> List[Dict]:
        return await self.search_pois_by_tags({
            "amenity": "place_of_worship",
            "religion": "hindu"
        })
    
    async def get_all_bali_pois(self) -> Dict[str, List[Dict]]:
        print("Fetching POIs from OpenStreetMap for Bali...")
        
        # Fetch all categories in parallel
        attractions, hotels, restaurants, beaches, temples = await asyncio.gather(
            self.get_bali_attractions(),
            self.get_bali_hotels(),
            self.get_bali_restaurants(),
            self.get_bali_beaches(),
            self.get_bali_temples(),
            return_exceptions=True
        )
        
        # Handle any exceptions
        def safe_result(result):
            return result if not isinstance(result, Exception) else []
        
        results = {
            "attractions": safe_result(attractions),
            "hotels": safe_result(hotels),
            "restaurants": safe_result(restaurants),
            "beaches": safe_result(beaches),
            "temples": safe_result(temples)
        }
        
        total = sum(len(v) for v in results.values())
        print(f"✅ Fetched {total} POIs from OpenStreetMap")
        
        return results
    
    def _parse_osm_element(self, element: Dict) -> Optional[Dict]:
        tags = element.get("tags", {})
        name = tags.get("name") or tags.get("name:en")
        
        if not name:
            return None
        
        # Get coordinates
        if element["type"] == "node":
            lat = element.get("lat")
            lon = element.get("lon")
        else:
            # For ways and relations, use center
            center = element.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")
        
        if not lat or not lon:
            return None
        
        # Check if within Bali bounds
        if not self._is_in_bali(lat, lon):
            return None
        
        return {
            "osm_id": element.get("id"),
            "osm_type": element.get("type"),
            "name": name,
            "name_en": tags.get("name:en"),
            "name_id": tags.get("name:id"),
            "latitude": lat,
            "longitude": lon,
            "tags": tags,
            "tourism_type": tags.get("tourism"),
            "amenity_type": tags.get("amenity"),
            "natural_type": tags.get("natural"),
            "religion": tags.get("religion"),
            "address": self._extract_address(tags),
            "phone": tags.get("phone") or tags.get("contact:phone"),
            "website": tags.get("website") or tags.get("contact:website"),
            "wikipedia": tags.get("wikipedia"),
            "wikidata": tags.get("wikidata"),
            "source": "openstreetmap"
        }
    
    def _is_in_bali(self, lat: float, lon: float) -> bool:
        return (
            self.bali_bbox[0] <= lat <= self.bali_bbox[2] and
            self.bali_bbox[1] <= lon <= self.bali_bbox[3]
        )
    
    def _extract_address(self, tags: Dict) -> Optional[str]:
        addr_parts = []
        
        if tags.get("addr:street"):
            addr_parts.append(tags["addr:street"])
        if tags.get("addr:city"):
            addr_parts.append(tags["addr:city"])
        if tags.get("addr:postcode"):
            addr_parts.append(tags["addr:postcode"])
        
        return ", ".join(addr_parts) if addr_parts else None
    
    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.nominatim_url}/search",
                    params={
                        "q": f"{address}, Bali, Indonesia",
                        "format": "json",
                        "limit": 1
                    },
                    headers={"User-Agent": self.user_agent},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                if data:
                    result = data[0]
                    lat = float(result["lat"])
                    lon = float(result["lon"])
                    
                    if self._is_in_bali(lat, lon):
                        return (lat, lon)
                
                return None
                
        except httpx.HTTPError as e:
            print(f"Geocoding error: {e}")
            return None
    
    def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth radius in km
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    
    def find_nearby_match(
        self,
        name: str,
        lat: float,
        lon: float,
        pois: List[Dict],
        max_distance_km: float = 0.5
    ) -> Optional[Dict]:
        from difflib import SequenceMatcher
        
        best_match = None
        best_score = 0
        
        for poi in pois:
            # Calculate name similarity
            poi_name = poi.get("name", "").lower()
            name_lower = name.lower()
            similarity = SequenceMatcher(None, poi_name, name_lower).ratio()
            
            # Calculate distance
            distance = self.calculate_distance(
                lat, lon,
                poi["latitude"], poi["longitude"]
            )
            
            # Combined score (70% name, 30% proximity)
            if distance <= max_distance_km:
                score = (similarity * 0.7) + ((max_distance_km - distance) / max_distance_km * 0.3)
                
                if score > best_score and score > 0.5:  # Minimum 50% match
                    best_score = score
                    best_match = poi
        
        return best_match


# Singleton instance
osm_service = OpenStreetMapService()
