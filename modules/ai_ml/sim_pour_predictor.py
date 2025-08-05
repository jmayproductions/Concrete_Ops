# modules/ai_ml/sim_pour_predictor.py

"""
ConcreteOps: Simulated Pour Predictor
Runs AI-powered simulations of future pours to detect forecasted delays, labor conflicts,
form reuse clashes, or weather hazards before they occur.
"""

import random
from shared.utils import log_event


class SimPourPredictor:
    def __init__(self, weather_api):
        self.weather_api = weather_api

    def simulate_pour(self, pour_schedule: list, crew_availability: dict) -> dict:
        """
        pour_schedule: List of dicts with keys:
            - 'pour_id', 'start_time', 'duration_hr', 'crew_type'
        crew_availability: Dict of crew_type to available hours that week
        """
        warnings = []
        time_overlaps = []
        weather_flags = []
        total_hours = {}

        for pour in pour_schedule:
            crew = pour["crew_type"]
            total_hours[crew] = total_hours.get(crew, 0) + pour["duration_hr"]

        # Check labor overload
        for crew, hours in total_hours.items():
            if hours > crew_availability.get(crew, 40):
                warnings.append(f"{crew} overbooked: {hours}h scheduled vs {crew_availability[crew]}h available")

        # Check overlapping pours (naive check)
        pour_schedule.sort(key=lambda x: x["start_time"])
        for i in range(1, len(pour_schedule)):
            prev = pour_schedule[i - 1]
            curr = pour_schedule[i]
            if curr["start_time"] < prev["start_time"] + prev["duration_hr"]:
                time_overlaps.append((prev["pour_id"], curr["pour_id"]))

        # Check weather risk (mock)
        for pour in pour_schedule:
            forecast = self.weather_api.get_forecast(pour["start_time"])
            if forecast.get("rain_chance", 0) > 0.6:
                weather_flags.append(f"Pour {pour['pour_id']} has high rain risk ({forecast['rain_chance']*100}%)")

        log_event(f"[SIM_POUR] {len(warnings)} warnings, {len(time_overlaps)} overlaps, {len(weather_flags)} weather risks")

        return {
            "labor_warnings": warnings,
            "overlap_warnings": time_overlaps,
            "weather_alerts": weather_flags,
            "status": "OK" if not (warnings or time_overlaps or weather_flags) else "REVIEW"
        }
