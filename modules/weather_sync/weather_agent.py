# modules/weather_sync/weather_agent.py

"""
ConcreteOps: Weather Agent
Syncs real-time and forecasted weather data from external API to inform pour scheduling, curing adjustments, and risk mitigation.
"""

import requests
from shared.utils import log_event, trigger_alert
from shared.config import WEATHER_API_URL, WEATHER_API_KEY, SITE_COORDS


class WeatherAgent:
    def __init__(self, pour_id):
        self.pour_id = pour_id

    def fetch_weather(self):
        params = {
            "lat": SITE_COORDS["lat"],
            "lon": SITE_COORDS["lon"],
            "appid": WEATHER_API_KEY,
            "units": "imperial"
        }
        try:
            response = requests.get(WEATHER_API_URL, params=params)
            response.raise_for_status()
            weather_data = response.json()
            log_event(f"[{self.pour_id}] Weather data retrieved.")
            return self._parse_weather(weather_data)
        except Exception as e:
            trigger_alert(f"[{self.pour_id}] Weather API failure: {e}")
            return None

    def _parse_weather(self, data):
        """
        Parses a 3-hour forecast into actionable weather indicators.
        """
        try:
            current = data["list"][0]
            return {
                "temp": current["main"]["temp"],
                "humidity": current["main"]["humidity"],
                "wind_speed": current["wind"]["speed"],
                "conditions": current["weather"][0]["description"]
            }
        except Exception as e:
            trigger_alert(f"[{self.pour_id}] Weather parsing error: {e}")
            return None
