# modules/gps_tracking/unit_tracker.py

"""
ConcreteOps: GPS Unit Tracker
Tracks location and ETA of all mobile units (mixers, pumpers, finishers, inspectors) via GPS integrations.
Provides real-time updates, route efficiency analysis, and links delays to pour timeline impact.
"""

import random
from datetime import datetime
from shared.utils import log_event


class UnitTracker:
    def __init__(self, project_id):
        self.project_id = project_id
        self.unit_positions = {}

    def update_position(self, unit_id: str, lat: float, lon: float, status: str = "en_route"):
        position = {
            "timestamp": datetime.now().isoformat(),
            "lat": lat,
            "lon": lon,
            "status": status
        }
        self.unit_positions[unit_id] = position
        log_event(f"[{self.project_id}] Updated GPS for {unit_id}: {position}")

    def get_unit_position(self, unit_id: str):
        return self.unit_positions.get(unit_id, None)

    def estimate_eta(self, unit_id: str, destination_coords=(0, 0)):
        # Placeholder ETA logic — replace with real routing API or model
        mock_eta = round(random.uniform(5, 30), 2)
        return {
            "unit_id": unit_id,
            "eta_minutes": mock_eta,
            "current_position": self.get_unit_position(unit_id)
        }

    def list_all_units(self):
        return list(self.unit_positions.keys())
