# modules/curing_monitor/curing_agent.py

"""
ConcreteOps: Curing Agent Module
Monitors real-time curing telemetry and adjusts the curing plan based on temperature, humidity, strength gain, and weather forecasts.
"""

from shared.utils import log_event, trigger_alert
from shared.config import CURING_THRESHOLDS


class CuringAgent:
    def __init__(self, pour_id):
        self.pour_id = pour_id
        self.telemetry = []

    def ingest_sensor_data(self, data: dict):
        """
        Example data:
        {
            "timestamp": "2025-08-03T12:34:56",
            "temperature": 72.5,
            "humidity": 48.3,
            "strength_estimate": 3100,
            "moisture_level": 0.92
        }
        """
        self.telemetry.append(data)
        log_event(f"[{self.pour_id}] Curing data ingested: {data}")

    def evaluate(self):
        if not self.telemetry:
            log_event(f"[{self.pour_id}] No curing data available.")
            return None

        latest = self.telemetry[-1]
        issues = []

        if latest["temperature"] < CURING_THRESHOLDS["min_temp"]:
            issues.append("Temperature too low")
        if latest["temperature"] > CURING_THRESHOLDS["max_temp"]:
            issues.append("Temperature too high")
        if latest["moisture_level"] < CURING_THRESHOLDS["min_moisture"]:
            issues.append("Dry curing conditions detected")

        if issues:
            for issue in issues:
                trigger_alert(f"[{self.pour_id}] Curing issue: {issue}")
            return {"status": "ALERT", "issues": issues, "latest": latest}

        log_event(f"[{self.pour_id}] Curing OK")
        return {"status": "OK", "latest": latest}
