import pytest
from modules.weather.weather_fetcher import WeatherFetcher

def test_weather_fetcher_init():
    fetcher = WeatherFetcher(lat=45.5152, lon=-122.6784)
    assert isinstance(fetcher, WeatherFetcher)
    assert fetcher.lat == 45.5152
    assert fetcher.lon == -122.6784

def test_fetch_weather_data(monkeypatch):
    # Mock API response
    def mock_get_weather(self):
        return {
            "temperature": 18.5,
            "humidity": 55,
            "wind_speed": 12.4,
            "precip_mm": 0.2,
            "forecast_safe": True
        }

    monkeypatch.setattr(WeatherFetcher, "get_weather", mock_get_weather)
    fetcher = WeatherFetcher(lat=45.5152, lon=-122.6784)
    data = fetcher.get_weather()

    assert isinstance(data, dict)
    assert "temperature" in data
    assert data["forecast_safe"] is True
