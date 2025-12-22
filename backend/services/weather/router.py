from fastapi import APIRouter
from services.weather.schemas import WeatherRequest, WeatherResponse
from services.weather.controller import get_weather_condition

router = APIRouter()

@router.post("/", response_model=WeatherResponse)
def get_weather(data: WeatherRequest):
    condition = get_weather_condition(data.location)

    return WeatherResponse(
        location=data.location,
        condition=condition
    )
