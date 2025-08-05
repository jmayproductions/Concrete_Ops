# modules/anchor_check/bolt_validator.py

"""
ConcreteOps: Anchor & Embed Validator
Checks placement of anchor bolts, embeds, hold-downs, and inserts against specified tolerances.
Prevents framing misalignment, misdrilled plates, and post-pour demolition.
"""

from shared.utils import log_event, trigger_alert
from shared.config import ANCHOR_TOLERANCES


class BoltValidator:
    def __init__(self, pour_id):
        self.pour_id = pour_id
        self.checks = []

    def record_anchor(self, location_id: str, x_dev: float, y_dev: float, z_dev: float):
        within_tolerance = (
            abs(x_dev) <= ANCHOR_TOLERANCES["x"] and
            abs(y_dev) <= ANCHOR_TOLERANCES["y"] and
            abs(z_dev) <= ANCHOR_TOLERANCES["z"]
        )
        result = {
            "location": location_id,
            "x_dev": x_dev,
            "y_dev": y_dev,
            "z_dev": z_dev,
            "passed": within_tolerance
        }
        self.checks.append(result)

        if not within_tolerance:
            trigger_alert(f"[{self.pour_id}] Anchor deviation at {location_id}: ({x_dev}, {y_dev}, {z_dev})")
        else:
            log_event(f"[{self.pour_id}] Anchor PASS at {location_id}")

    def summary(self):
        total = len(self.checks)
        failed = len([c for c in self.checks if not c["passed"]])
        return {
            "total_points": total,
            "failures": failed,
            "passed": total - failed
        }
