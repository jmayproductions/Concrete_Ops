# modules/slab_profile/slab_evaluator.py

"""
ConcreteOps: Slab Evaluator
Analyzes slab profile data to check against FF/FL tolerances, track floor deviations, and identify finishing issues.
"""

from shared.utils import log_event, trigger_alert
from shared.config import SLAB_TOLERANCES


class SlabEvaluator:
    def __init__(self, pour_id):
        self.pour_id = pour_id
        self.elevation_data = []  # list of dicts with GPS/laser data

    def record_point(self, x: float, y: float, elevation: float):
        self.elevation_data.append({"x": x, "y": y, "elevation": elevation})
        log_event(f"[{self.pour_id}] Slab point recorded at ({x}, {y}) = {elevation} in")

    def evaluate(self):
        if not self.elevation_data:
            return None

        elevations = [p["elevation"] for p in self.elevation_data]
        max_dev = max(elevations) - min(elevations)

        if max_dev > SLAB_TOLERANCES["max_variation"]:
            trigger_alert(f"[{self.pour_id}] Slab flatness out of tolerance: Δ = {max_dev:.2f} in")

        return {
            "total_points": len(elevations),
            "max_variation": round(max_dev, 3)
        }
