"""
fetch_weather.py
────────────────
Weather data fetching utilities using Open-Meteo API.
"""
import requests
from config import LATITUDE, LONGITUDE, API_URL


def fetch_weather():
    """
    Fetch current weather data from Open-Meteo API.
    Returns temperature, radiation, and weather code.
    """
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,shortwave_radiation,weathercode"
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "temperature": data["current"]["temperature_2m"],
            "radiation": data["current"]["shortwave_radiation"],
            "weathercode": data["current"]["weathercode"]
        }
    except requests.exceptions.RequestException as e:
        print(f"Weather API error: {e}")
        return None


def fetch_weather_by_datetime(date: str, hour: int):
    """
    Fetch historical or forecast weather data for a specific date and hour.
    Returns temperature, radiation, and weather code for that time.
    """
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "temperature_2m,shortwave_radiation,weathercode",
        "start_date": date,
        "end_date": date,
        "timezone": "auto"
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Check for API error
        if "error" in data:
            print(f"API Error: {data.get('reason', 'Unknown error')}")
            return None

        hourly = data.get("hourly")
        if not hourly:
            print("No hourly data returned")
            return None

        # Safely get index (hour 0-23)
        time_index = min(hour, len(hourly["temperature_2m"]) - 1)

        return {
            "temperature": hourly["temperature_2m"][time_index],
            "radiation": hourly["shortwave_radiation"][time_index],
            "weathercode": hourly["weathercode"][time_index]
        }
    except requests.exceptions.RequestException as e:
        print(f"Weather API error: {e}")
        return None
