# modules/weather_monitor/wx_agent.py

"""
ConcreteOps: Weather Agent
Tracks real-time weather data from API integrations to inform pour decisions, curing conditions, and delay mitigation.
Includes alerting logic for rain, heat, cold, or wind events.
"""

import requests
from shared.utils import log_event, trigger_alert
from shared.config import WEATHER_API_KEY, WEATHER_API_URL


class WeatherAgent:
    def __init__(self, location_coords):
        self.coords = location_coords  # (lat, lon)

    def fetch_forecast(self):
        lat, lon = self.coords
        url = f"{WEATHER_API_URL}?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=imperial"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            log_event(f"Weather data pulled for ({lat}, {lon})")
            return self._parse(data)
        else:
            trigger_alert("Weather API fetch failed.")
            return None

    def _parse(self, data):
        # Extract key fields (first 6 hours forecast)
        forecast = data["list"][0]
        wx = {
            "temp": forecast["main"]["temp"],
            "humidity": forecast["main"]["humidity"],
            "wind_speed": forecast["wind"]["speed"],
            "conditions": forecast["weather"][0]["description"]
        }

        self._alert_logic(wx)
        return wx

    def _alert_logic(self, wx):
        if wx["temp"] < 35:
            trigger_alert("Cold weather alert – potential freeze risk during pour/curing.")
        if wx["temp"] > 90:
            trigger_alert("Heat alert – implement hot-weather pour protocol.")
        if "rain" in wx["conditions"].lower():
            trigger_alert("Rain in forecast – cover slabs or delay pour.")
        if wx["wind_speed"] > 25:
            trigger_alert("High winds – risk for flying debris or pour finish issues.")
