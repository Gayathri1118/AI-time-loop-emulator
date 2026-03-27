"""
phase1_data.py
──────────────
Phase 1: Data collection from weather API.
Fetches weather data for the specified input date/hour.
"""
from utils.fetch_weather import fetch_weather, fetch_weather_by_datetime


def get_environment_data(input_date: str, input_hour: int):
    """
    Fetch environment data for the specified date and hour.
    Falls back to current weather if historical/forecast data is unavailable.
    
    Args:
        input_date: Date string in YYYY-MM-DD format
        input_hour: Hour of day (0-23)
    
    Returns:
        Dictionary with temperature, radiation, weathercode
    """
    # Try to fetch weather for the specified date/hour
    past = fetch_weather_by_datetime(input_date, input_hour)
    
    # Also fetch current weather for comparison
    current = fetch_weather()

    # Use past data if available, otherwise fall back to current
    if past is None:
        print(f"Using fallback (current weather only for {input_date} {input_hour}:00)")
        weather_data = current
    else:
        weather_data = past

    if weather_data is None:
        return {"error": "Unable to fetch weather data"}

    return {
        "input_date_weather": weather_data,
        "current_weather": current,
        "temperature": weather_data["temperature"],
        "radiation": weather_data["radiation"],
        "weathercode": weather_data["weathercode"]
    }
