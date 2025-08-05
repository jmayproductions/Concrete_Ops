# modules/ai_ml/flex_schedule_optimizer.py

"""
ConcreteOps: Flex Schedule Optimizer
Uses AI heuristics and environmental data to dynamically optimize concrete pour schedules
based on weather forecasts, crew availability, equipment conflicts, and material delivery windows.
"""

import random
from datetime import datetime, timedelta
from shared.utils import log_event


class FlexScheduleOptimizer:
    def __init__(self, weather_api, crew_api, equipment_api, materials_api):
        self.weather_api = weather_api
        self.crew_api = crew_api
        self.equipment_api = equipment_api
        self.materials_api = materials_api

    def generate_schedule(self, start_date: str, pour_windows: list) -> list:
        optimized = []
        for window in pour_windows:
            slot = self._evaluate_window(start_date, window)
            optimized.append(slot)
        log_event(f"[SCHEDULER] Generated flex schedule with {len(optimized)} windows")
        return optimized

    def _evaluate_window(self, base_date: str, window: dict) -> dict:
        date_obj = datetime.strptime(base_date, "%Y-%m-%d")
        window_days = window.get("duration_days", 1)
        preferred_temp = window.get("ideal_temp_range", (45, 80))
        crew_count = self.crew_api.get_available_crews(date_obj, window_days)
        weather = self.weather_api.forecast(date_obj, window_days)
        equipment_ready = self.equipment_api.check_availability(date_obj, window_days)
        material_confirmed = self.materials_api.delivery_window(date_obj, window_days)

        rating = 0
        if preferred_temp[0] <= weather["avg_temp"] <= preferred_temp[1]:
            rating += 1
        if crew_count >= window.get("min_crew", 2):
            rating += 1
        if equipment_ready:
            rating += 1
        if material_confirmed:
            rating += 1

        return {
            "window_start": base_date,
            "duration_days": window_days,
            "weather_ok": weather,
            "crew_ok": crew_count,
            "equipment_ok": equipment_ready,
            "materials_ok": material_confirmed,
            "rating": rating,
            "score": round(rating / 4, 2)
        }
