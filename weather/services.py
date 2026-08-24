import math
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
FLOOD_URL = "https://flood-api.open-meteo.com/v1/flood"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def geocode_city(query):
    response = requests.get(
        GEOCODING_URL,
        params={"name": query, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    if not results:
        raise ValueError(f"Location '{query}' was not found.")
    return results[0]


def get_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "forecast_days": 7,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature," 
            "precipitation,rain,weather_code,wind_speed_10m,pressure_msl"
        ),
        "hourly": (
            "temperature_2m,relative_humidity_2m,precipitation_probability,"
            "precipitation,rain,weather_code,wind_speed_10m"
        ),
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_sum,rain_sum,precipitation_probability_max,"
            "wind_speed_10m_max"
        ),
    }
    response = requests.get(WEATHER_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def get_flood(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "river_discharge,river_discharge_mean,river_discharge_p75,river_discharge_max",
        "forecast_days": 7,
        "timezone": "auto",
    }
    response = requests.get(FLOOD_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def safe_number(value, default=0.0):
    if value is None:
        return default
    try:
        value = float(value)
        return default if math.isnan(value) else value
    except (TypeError, ValueError):
        return default


def calculate_flood_risk(daily_weather, flood_data):
    """Demo indicator, NOT an official flood-warning model."""
    rain = safe_number(daily_weather.get("precipitation_sum", [0])[0])
    rain_prob = safe_number(daily_weather.get("precipitation_probability_max", [0])[0])

    discharge = safe_number(flood_data.get("daily", {}).get("river_discharge", [0])[0])
    p75 = safe_number(flood_data.get("daily", {}).get("river_discharge_p75", [0])[0])
    max_q = safe_number(flood_data.get("daily", {}).get("river_discharge_max", [0])[0])

    score = 0
    reasons = []

    if rain >= 100:
        score += 40
        reasons.append("Very heavy forecast rainfall")
    elif rain >= 50:
        score += 30
        reasons.append("Heavy forecast rainfall")
    elif rain >= 25:
        score += 18
        reasons.append("Moderate-to-heavy forecast rainfall")
    elif rain >= 10:
        score += 8
        reasons.append("Meaningful forecast rainfall")

    if rain_prob >= 80:
        score += 20
        reasons.append("High precipitation probability")
    elif rain_prob >= 60:
        score += 12
        reasons.append("Elevated precipitation probability")
    elif rain_prob >= 40:
        score += 6

    if p75 > 0:
        ratio = discharge / p75
        if ratio >= 1.5:
            score += 30
            reasons.append("River discharge is well above the ensemble 75th percentile")
        elif ratio >= 1.15:
            score += 20
            reasons.append("River discharge is above the ensemble 75th percentile")
        elif ratio >= 0.9:
            score += 10
            reasons.append("River discharge is near the ensemble upper range")
    elif max_q > 0 and discharge / max_q >= 0.75:
        score += 15
        reasons.append("River discharge is near the forecast maximum")

    score = min(score, 100)
    if score >= 70:
        level = "Severe"
        css = "severe"
    elif score >= 50:
        level = "High"
        css = "high"
    elif score >= 25:
        level = "Moderate"
        css = "moderate"
    else:
        level = "Low"
        css = "low"

    if not reasons:
        reasons.append("No strong rainfall or river-discharge signal in the available forecast")

    return {
        "score": score,
        "level": level,
        "css": css,
        "rain_mm": round(rain, 1),
        "rain_probability": round(rain_prob),
        "river_discharge": round(discharge, 2),
        "river_p75": round(p75, 2),
        "reasons": reasons[:3],
    }


def weather_code_text(code):
    mapping = {
        0: ("Clear sky", "☀️"),
        1: ("Mainly clear", "🌤️"),
        2: ("Partly cloudy", "⛅"),
        3: ("Overcast", "☁️"),
        45: ("Fog", "🌫️"),
        48: ("Rime fog", "🌫️"),
        51: ("Light drizzle", "🌦️"),
        53: ("Drizzle", "🌦️"),
        55: ("Heavy drizzle", "🌧️"),
        61: ("Light rain", "🌦️"),
        63: ("Rain", "🌧️"),
        65: ("Heavy rain", "🌧️"),
        71: ("Light snow", "🌨️"),
        73: ("Snow", "🌨️"),
        75: ("Heavy snow", "❄️"),
        80: ("Rain showers", "🌦️"),
        81: ("Rain showers", "🌧️"),
        82: ("Heavy rain showers", "⛈️"),
        95: ("Thunderstorm", "⛈️"),
        96: ("Thunderstorm with hail", "⛈️"),
        99: ("Thunderstorm with heavy hail", "⛈️"),
    }
    return mapping.get(int(code or 0), ("Unknown", "🌡️"))


def build_dashboard(city):
    location = geocode_city(city)
    lat, lon = location["latitude"], location["longitude"]
    weather = get_weather(lat, lon)
    flood = get_flood(lat, lon)

    current = weather["current"]
    current_desc, current_icon = weather_code_text(current.get("weather_code"))
    daily = weather["daily"]
    hourly = weather["hourly"]

    daily_items = []
    for i, day in enumerate(daily["time"]):
        desc, icon = weather_code_text(daily["weather_code"][i])
        daily_items.append({
            "date": day,
            "label": datetime.fromisoformat(day).strftime("%a"),
            "icon": icon,
            "description": desc,
            "max": round(safe_number(daily["temperature_2m_max"][i])),
            "min": round(safe_number(daily["temperature_2m_min"][i])),
            "rain": round(safe_number(daily["precipitation_sum"][i]), 1),
            "probability": round(safe_number(daily["precipitation_probability_max"][i])),
            "wind": round(safe_number(daily["wind_speed_10m_max"][i])),
        })

    # First 24 hourly points for a compact chart.
    hourly_items = []
    for i in range(min(24, len(hourly["time"]))):
        hour = datetime.fromisoformat(hourly["time"][i])
        hourly_items.append({
            "time": hour.strftime("%H:%M"),
            "temperature": round(safe_number(hourly["temperature_2m"][i]), 1),
            "probability": round(safe_number(hourly["precipitation_probability"][i])),
            "rain": round(safe_number(hourly["precipitation"][i]), 1),
        })

    flood_risk = calculate_flood_risk(daily, flood)

    return {
        "location": {
            "name": location.get("name", city),
            "country": location.get("country", ""),
            "admin1": location.get("admin1", ""),
            "latitude": lat,
            "longitude": lon,
        },
        "current": {
            "temperature": round(safe_number(current.get("temperature_2m"))),
            "feels_like": round(safe_number(current.get("apparent_temperature"))),
            "humidity": round(safe_number(current.get("relative_humidity_2m"))),
            "wind": round(safe_number(current.get("wind_speed_10m"))),
            "pressure": round(safe_number(current.get("pressure_msl"))),
            "rain": round(safe_number(current.get("precipitation")), 1),
            "description": current_desc,
            "icon": current_icon,
        },
        "daily": daily_items,
        "hourly": hourly_items,
        "flood": flood_risk,
        "timezone": weather.get("timezone", "auto"),
    }
