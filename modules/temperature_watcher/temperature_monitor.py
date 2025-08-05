# modules/temperature_watcher/temperature_monitor.py

"""
ConcreteOps: Temperature Monitor
Tracks pour temperature and ambient readings to identify high-risk thermal conditions that can affect set time and strength gain.
"""

from shared.utils import log_event, trigger_alert
from shared.config import TEMPERATURE_THRESHOLDS


class TemperatureMonitor:
    def __init__(self, pour_id):
        self.pour_id = pour_id
        self.readings = []

    def ingest(self, data: dict):
        """
        Example:
        {
            "timestamp": "2025-08-04T10:00:00",
            "concrete_temp": 91.5,
            "ambient_temp": 95.3,
            "humidity": 28.0
        }
        """
        self.readings.append(data)
        log_event(f"[{self.pour_id}] Temperature reading: {data}")
        self._check_thresholds(data)

    def _check_thresholds(self, data):
        issues = []

        if data["concrete_temp"] > TEMPERATURE_THRESHOLDS["max_concrete_temp"]:
            issues.append(f"Concrete too hot: {data['concrete_temp']}°F")
        if data["ambient_temp"] > TEMPERATURE_THRESHOLDS["max_ambient_temp"]:
            issues.append(f"Ambient too hot: {data['ambient_temp']}°F")
        if data["humidity"] < TEMPERATURE_THRESHOLDS["min_humidity"]:
            issues.append(f"Low humidity: {data['humidity']}%")

        if issues:
            for issue in issues:
                trigger_alert(f"[{self.pour_id}] Temp alert: {issue}")
        else:
            log_event(f"[{self.pour_id}] Temperature within acceptable limits")

    def get_latest(self):
        return self.readings[-1] if self.readings else None
