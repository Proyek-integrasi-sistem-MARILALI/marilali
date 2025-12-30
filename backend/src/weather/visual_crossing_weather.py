import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from src.config import settings


class VisualCrossingWeatherService:
    def __init__(self):
        self.api_key = settings.VISUAL_CROSSING_API_KEY
        self.base_url = settings.VISUAL_CROSSING_API_URL
        self.default_location = "Bali,Indonesia"
    
    async def get_forecast(
        self,
        location: str = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[Dict]:
        if not self.api_key:
            print("Visual Crossing API key not configured")
            return self._get_mock_forecast()
        
        location = location or self.default_location
        
        # Build timeline URL
        if start_date and end_date:
            url = f"{self.base_url}/{location}/{start_date}/{end_date}"
        else:
            # Next 7 days
            url = f"{self.base_url}/{location}"
        
        params = {
            "key": self.api_key,
            "unitGroup": "metric",
            "include": "days,current",
            "elements": "datetime,temp,tempmax,tempmin,humidity,precip,windspeed,conditions,description,icon"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                return self._normalize_response(data)
                
        except httpx.HTTPError as e:
            print(f"Weather API error: {e}")
            return self._get_mock_forecast()
    
    async def get_current_weather(self, location: str = None) -> Optional[Dict]:
        """Get current weather conditions."""
        forecast = await self.get_forecast(location)
        if forecast and forecast.get("current"):
            return forecast["current"]
        return None
    
    async def get_daily_forecast(
        self,
        location: str = None,
        days: int = 7
    ) -> List[Dict]:
        forecast = await self.get_forecast(location)
        if forecast and forecast.get("days"):
            return forecast["days"][:days]
        return []
    
    async def is_good_weather_for_activity(
        self,
        activity_type: str,
        location: str = None,
        date: str = None
    ) -> bool:
        forecast = await self.get_forecast(location, date, date)
        if not forecast or not forecast.get("days"):
            return True  # Assume okay if no data
        
        day = forecast["days"][0]
        temp = day.get("temp", 28)
        precip = day.get("precip", 0)
        conditions = day.get("conditions", "").lower()
        
        # Activity-specific rules
        if activity_type == "beach":
            return temp >= 25 and precip < 5 and "rain" not in conditions
        elif activity_type == "hiking":
            return temp <= 32 and precip < 2 and "storm" not in conditions
        elif activity_type == "temple":
            return precip < 10  # Temples okay with light rain
        elif activity_type == "indoor":
            return True  # Indoor activities always okay
        else:
            return precip < 15  # General threshold
    
    def _normalize_response(self, raw_data: Dict) -> Dict:
        return {
            "location": raw_data.get("resolvedAddress", "Bali, Indonesia"),
            "timezone": raw_data.get("timezone", "Asia/Makassar"),
            "current": self._parse_current(raw_data.get("currentConditions")),
            "days": [self._parse_day(day) for day in raw_data.get("days", [])]
        }
    
    def _parse_current(self, current: Optional[Dict]) -> Optional[Dict]:
        """Parse current conditions."""
        if not current:
            return None
        
        return {
            "datetime": current.get("datetime"),
            "temp": current.get("temp"),
            "humidity": current.get("humidity"),
            "precip": current.get("precip", 0),
            "windspeed": current.get("windspeed"),
            "conditions": current.get("conditions"),
            "icon": current.get("icon")
        }
    
    def _parse_day(self, day: Dict) -> Dict:
        return {
            "date": day.get("datetime"),
            "temp": day.get("temp"),
            "temp_max": day.get("tempmax"),
            "temp_min": day.get("tempmin"),
            "humidity": day.get("humidity"),
            "precip": day.get("precip", 0),
            "windspeed": day.get("windspeed"),
            "conditions": day.get("conditions"),
            "description": day.get("description"),
            "icon": day.get("icon")
        }
    
    def _get_mock_forecast(self) -> Dict:
        today = datetime.now()
        
        return {
            "location": "Bali, Indonesia",
            "timezone": "Asia/Makassar",
            "current": {
                "datetime": today.strftime("%H:%M:%S"),
                "temp": 28,
                "humidity": 75,
                "precip": 0,
                "windspeed": 12,
                "conditions": "Partly cloudy",
                "icon": "partly-cloudy-day"
            },
            "days": [
                {
                    "date": (today + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "temp": 27 + i % 3,
                    "temp_max": 30 + i % 3,
                    "temp_min": 24 + i % 2,
                    "humidity": 70 + i * 2,
                    "precip": 0 if i % 3 != 0 else 5,
                    "windspeed": 10 + i,
                    "conditions": "Sunny" if i % 3 != 0 else "Light rain",
                    "description": "Pleasant tropical weather" if i % 3 != 0 else "Afternoon showers possible",
                    "icon": "clear-day" if i % 3 != 0 else "rain"
                }
                for i in range(7)
            ]
        }


# Singleton instance
weather_service = VisualCrossingWeatherService()
