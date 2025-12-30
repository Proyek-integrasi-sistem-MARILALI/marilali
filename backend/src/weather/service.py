from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from fastapi import HTTPException

from src.weather.weather_models import Weather
from src.weather.weather_alert_models import WeatherAlert
from src.weather.weather_alert_models import WeatherBasedRecommendation
from src.destination.models import Destination
from src.weather.visual_crossing_weather import weather_service as vc_weather
from src.config import settings


async def get_weather_forecast(
    location: str,
    destination_id: Optional[int],
    days: int,
    db: AsyncSession
) -> Dict:
    # Check cache first
    cached_weather = await _get_cached_weather(location, db)
    if cached_weather:
        return _format_weather_response(cached_weather)
    
    # Fetch from weather API
    weather_data = await _fetch_weather_from_api(location, days)
    
    if not weather_data:
        raise HTTPException(status_code=404, detail="Weather data not available for this location")
    
    # Save to database
    weather_record = Weather(
        destination_id=destination_id,
        location=location,
        date=datetime.utcnow().date(),
        temperature_avg=weather_data.get("current_temp"),
        condition=weather_data.get("condition"),
        description=weather_data.get("description"),
        humidity=weather_data.get("humidity"),
        wind_speed=weather_data.get("wind_speed"),
        precipitation=weather_data.get("precipitation", 0)
    )
    
    db.add(weather_record)
    await db.commit()
    await db.refresh(weather_record)
    
    return weather_data


async def _fetch_weather_from_api(location: str, days: int) -> Optional[Dict]:
    try:
        # Use Visual Crossing Weather Service
        forecast_data = await vc_weather.get_forecast(location=location)
        
        if not forecast_data:
            return None
        
        # Extract current and daily forecast
        current = forecast_data.get("current", {})
        days_data = forecast_data.get("days", [])[:days]
        
        return {
            "location": forecast_data.get("location", location),
            "current_temp": current.get("temp"),
            "condition": current.get("conditions"),
            "description": days_data[0].get("description") if days_data else None,
            "humidity": current.get("humidity"),
            "wind_speed": current.get("windspeed"),
            "precipitation": current.get("precip", 0),
            "forecast": _parse_visual_crossing_forecast(days_data)
        }
            
    except Exception as e:
        print(f"Visual Crossing Weather API error: {e}")
        return None


def _parse_visual_crossing_forecast(days_data: List[Dict]) -> List[Dict]:
    forecast = []
    
    for day in days_data:
        forecast.append({
            "date": day.get("date"),
            "temp_min": day.get("temp_min"),
            "temp_max": day.get("temp_max"),
            "temp_avg": day.get("temp"),
            "condition": day.get("conditions"),
            "description": day.get("description"),
            "humidity": day.get("humidity"),
            "precipitation": day.get("precip", 0),
            "wind_speed": day.get("windspeed"),
            "icon": day.get("icon")
        })
    
    return forecast


def _get_mock_weather_data(location: str, days: int) -> Dict:
    base_temp = 25.0
    
    forecast = []
    for i in range(days):
        day = datetime.utcnow().date() + timedelta(days=i)
        forecast.append({
            "date": day.isoformat(),
            "temp_min": base_temp - 3,
            "temp_max": base_temp + 5,
            "temp_avg": base_temp,
            "condition": "Clear" if i % 2 == 0 else "Clouds",
            "description": "clear sky" if i % 2 == 0 else "scattered clouds"
        })
    
    return {
        "location": location,
        "current_temp": base_temp,
        "condition": "Clear",
        "description": "clear sky",
        "humidity": 65,
        "wind_speed": 3.5,
        "forecast": forecast,
        "source": "mock_data"
    }


async def _get_cached_weather(location: str, db: AsyncSession) -> Optional[Weather]:
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    result = await db.execute(
        select(Weather)
        .where(
            and_(
                Weather.location == location,
                Weather.created_at >= one_hour_ago
            )
        )
        .order_by(Weather.created_at.desc())
    )
    
    return result.scalar_one_or_none()


def _format_weather_response(weather: Weather) -> Dict:
    return {
        "location": weather.location,
        "current_temp": weather.temperature_avg,
        "condition": weather.condition,
        "description": weather.description,
        "humidity": weather.humidity,
        "wind_speed": weather.wind_speed,
        "precipitation": weather.precipitation,
        "forecast": [],
        "source": "cached"
    }


async def create_weather_alert(
    user_id: int,
    destination_id: int,
    alert_type: str,
    threshold_value: float,
    db: AsyncSession
) -> WeatherAlert:
    alert = WeatherAlert(
        user_id=user_id,
        destination_id=destination_id,
        alert_type=alert_type,
        threshold_value=threshold_value,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    return alert


async def get_user_weather_alerts(
    user_id: int,
    db: AsyncSession,
    active_only: bool = True
) -> List[WeatherAlert]:
    query = select(WeatherAlert).where(WeatherAlert.user_id == user_id)
    
    if active_only:
        query = query.where(WeatherAlert.is_active == True)
    
    result = await db.execute(query.order_by(WeatherAlert.created_at.desc()))
    return list(result.scalars().all())


async def check_weather_alerts(
    user_id: int,
    destination_id: int,
    current_weather: Dict,
    db: AsyncSession
) -> List[Dict]:
    # Get active alerts for this destination
    alerts = await db.execute(
        select(WeatherAlert).where(
            and_(
                WeatherAlert.user_id == user_id,
                WeatherAlert.destination_id == destination_id,
                WeatherAlert.is_active == True
            )
        )
    )
    
    triggered_alerts = []
    
    for alert in alerts.scalars().all():
        triggered = False
        
        if alert.alert_type == "temperature_high":
            if current_weather.get("current_temp", 0) > alert.threshold_value:
                triggered = True
        elif alert.alert_type == "temperature_low":
            if current_weather.get("current_temp", 100) < alert.threshold_value:
                triggered = True
        elif alert.alert_type == "rain" and current_weather.get("condition") == "Rain":
            triggered = True
        elif alert.alert_type == "storm" and current_weather.get("condition") in ["Thunderstorm", "Tornado"]:
            triggered = True
        
        if triggered:
            triggered_alerts.append({
                "alert_id": alert.id,
                "alert_type": alert.alert_type,
                "message": f"Weather alert: {alert.alert_type} threshold reached",
                "current_value": current_weather.get("current_temp"),
                "threshold": alert.threshold_value
            })
    
    return triggered_alerts


async def get_weather_based_recommendations(
    destination_id: int,
    travel_date: datetime.date,
    db: AsyncSession
) -> List[str]:
    # Get destination
    dest_result = await db.execute(
        select(Destination).where(Destination.id == destination_id)
    )
    destination = dest_result.scalar_one_or_none()
    
    if not destination:
        return []
    
    # Get weather forecast
    weather_data = await get_weather_forecast(
        location=f"{destination.city}, {destination.country}",
        destination_id=destination_id,
        days=7,
        db=db
    )
    
    recommendations = []
    
    # Analyze forecast for travel date
    for day_forecast in weather_data.get("forecast", []):
        if day_forecast["date"] == travel_date.isoformat():
            temp_avg = day_forecast["temp_avg"]
            condition = day_forecast["condition"]
            
            # Temperature recommendations
            if temp_avg > 30:
                recommendations.append("Hot weather expected - pack light, breathable clothing and sunscreen")
            elif temp_avg < 10:
                recommendations.append("Cold weather expected - pack warm clothing and layers")
            else:
                recommendations.append("Pleasant weather expected - ideal for outdoor activities")
            
            # Condition recommendations
            if condition == "Rain":
                recommendations.append("Rain expected - bring waterproof gear and plan indoor activities")
            elif condition == "Clear":
                recommendations.append("Clear skies - perfect for sightseeing and outdoor exploration")
            elif condition == "Clouds":
                recommendations.append("Cloudy weather - good for photography with soft lighting")
            elif condition == "Snow":
                recommendations.append(" Snow expected - pack winter gear and check transport conditions")
            
            break
    
    if not recommendations:
        recommendations.append("Check weather forecast closer to your travel date")
    
    return recommendations


async def delete_weather_alert(
    alert_id: int,
    user_id: int,
    db: AsyncSession
) -> Dict:
    result = await db.execute(
        select(WeatherAlert).where(
            and_(
                WeatherAlert.id == alert_id,
                WeatherAlert.user_id == user_id
            )
        )
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    await db.delete(alert)
    await db.commit()
    
    return {"message": "Weather alert deleted successfully"}
