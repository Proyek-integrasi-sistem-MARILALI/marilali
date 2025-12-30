
from typing import Dict, Any, List
from datetime import datetime, timedelta


def analyze_weather_for_travel(weather_data: Dict, travel_dates: List[datetime]) -> Dict[str, Any]:
    analysis = {
        "is_favorable": True,
        "warnings": [],
        "recommendations": [],
        "best_activities": [],
        "weather_score": 0.0
    }
    
    # Analyze temperature
    temp = weather_data.get("temperature", 25)
    if temp < 10:
        analysis["warnings"].append("Cold weather expected. Pack warm clothing.")
        analysis["best_activities"].append("Indoor museums and cafes")
    elif temp > 35:
        analysis["warnings"].append("Very hot weather. Stay hydrated.")
        analysis["best_activities"].append("Water activities and indoor attractions")
    else:
        analysis["best_activities"].extend(["Outdoor sightseeing", "Hiking", "Beach activities"])
    
    # Analyze precipitation
    precipitation = weather_data.get("precipitation_probability", 0)
    if precipitation > 70:
        analysis["warnings"].append("High chance of rain. Bring umbrella.")
        analysis["recommendations"].append("Plan indoor activities")
        analysis["is_favorable"] = False
    elif precipitation > 40:
        analysis["recommendations"].append("Have backup indoor plans")
    
    # Calculate weather score (0-1)
    temp_score = max(0, min(1, 1 - abs(temp - 25) / 25))
    rain_score = 1 - (precipitation / 100)
    analysis["weather_score"] = round((temp_score + rain_score) / 2, 2)
    
    return analysis


def suggest_best_travel_dates(weather_forecast: List[Dict], desired_days: int) -> Dict[str, Any]:
    if not weather_forecast:
        return {"suggested_dates": [], "reason": "No weather data available"}
    
    # Score each date
    scored_dates = []
    for day in weather_forecast:
        date = day.get("date")
        temp = day.get("temperature", 25)
        rain = day.get("precipitation_probability", 0)
        
        score = (1 - abs(temp - 25) / 25) * (1 - rain / 100)
        scored_dates.append({"date": date, "score": score, "temp": temp, "rain": rain})
    
    # Sort by score
    scored_dates.sort(key=lambda x: x["score"], reverse=True)
    
    # Find consecutive days with good weather
    best_dates = scored_dates[:desired_days]
    avg_score = sum(d["score"] for d in best_dates) / len(best_dates)
    
    return {
        "suggested_dates": [d["date"] for d in best_dates],
        "average_weather_score": round(avg_score, 2),
        "reason": "Selected dates with optimal weather conditions"
    }


def check_weather_compatibility(activity_type: str, weather: Dict) -> bool:
    temp = weather.get("temperature", 25)
    rain = weather.get("precipitation_probability", 0)
    
    outdoor_activities = ["hiking", "beach", "sightseeing", "trekking", "camping"]
    indoor_activities = ["museum", "shopping", "restaurant", "spa", "theater"]
    
    if activity_type.lower() in outdoor_activities:
        return rain < 50 and 15 < temp < 35
    elif activity_type.lower() in indoor_activities:
        return True
    
    return True  # Default to compatible


def get_packing_suggestions(weather_forecast: List[Dict]) -> List[str]:
    suggestions = ["Passport and travel documents", "Phone charger", "Medications"]
    
    if not weather_forecast:
        return suggestions
    
    temps = [w.get("temperature", 25) for w in weather_forecast]
    rains = [w.get("precipitation_probability", 0) for w in weather_forecast]
    
    avg_temp = sum(temps) / len(temps)
    max_rain = max(rains)
    
    if avg_temp < 15:
        suggestions.extend(["Warm jacket", "Long pants", "Sweater"])
    elif avg_temp > 30:
        suggestions.extend(["Light clothing", "Sunscreen", "Hat", "Sunglasses"])
    else:
        suggestions.extend(["Light jacket", "Comfortable clothing"])
    
    if max_rain > 40:
        suggestions.extend(["Umbrella", "Rain jacket", "Waterproof bag"])
    
    return suggestions
