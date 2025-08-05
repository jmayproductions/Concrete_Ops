# modules/sensor_fusion_core/fusion_engine.py

"""
ConcreteOps: Sensor Fusion Core
Combines input from multiple field sensors (temperature, slump, moisture, strength, GPS) into a unified data stream
for downstream validation, alerting, and analytics.
"""

from shared.utils import log_event


class FusionEngine:
    def __init__(self, pour_id):
        self.pour_id = pour_id
        self.snapshots = []

    def ingest(self, sensor_payload: dict):
        """
        Example payload:
        {
            "timestamp": "2025-08-04T14:30:00",
            "temperature": 87.1,
            "slump": 4.75,
            "strength": 3100,
            "moisture": 0.91,
            "gps": {"lat": 45.5123, "lon": -122.6587}
        }
        """
        self.snapshots.append(sensor_payload)
        log_event(f"[{self.pour_id}] Sensor fusion snapshot received.")
        return True

    def latest_snapshot(self):
        if not self.snapshots:
            return None
        return self.snapshots[-1]

    def average_metrics(self):
        if not self.snapshots:
            return {}

        keys = ["temperature", "slump", "strength", "moisture"]
        totals = {k: 0.0 for k in keys}
        count = len(self.snapshots)

        for snap in self.snapshots:
            for k in keys:
                if k in snap:
                    totals[k] += snap[k]

        return {k: round(totals[k] / count, 2) for k in keys}
