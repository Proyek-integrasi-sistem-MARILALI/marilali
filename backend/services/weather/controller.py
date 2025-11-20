def get_weather_condition(location: str):
    """
    Mock weather system: nanti bisa diganti OpenWeather API.
    """
    mock_weather_map = {
        "Kuta": "sunny",
        "Denpasar": "cloudy",
        "Ubud": "rainy",
        "Canggu": "sunny",
        "Sanur": "cloudy",
    }

    return mock_weather_map.get(location, "sunny")
