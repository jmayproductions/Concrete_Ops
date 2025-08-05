# modules/slump_detector/slump_checker.py

"""
ConcreteOps: Slump Checker
Evaluates real-time slump measurements against configured limits and triggers alerts if values deviate from specification.
"""

from shared.utils import log_event, trigger_alert
from shared.config import SLUMP_RANGE


class SlumpChecker:
    def __init__(self, pour_id):
        self.pour_id = pour_id
        self.readings = []

    def add_slump(self, value: float):
        """
        value: slump in inches (e.g. 4.75)
        """
        self.readings.append(value)
        log_event(f"[{self.pour_id}] Slump reading added: {value} in")

        if not self._within_range(value):
            trigger_alert(f"[{self.pour_id}] Slump out of spec: {value} in")

    def _within_range(self, value: float) -> bool:
        return SLUMP_RANGE["min"] <= value <= SLUMP_RANGE["max"]

    def get_status(self):
        if not self.readings:
            return "NO DATA"

        last = self.readings[-1]
        if self._within_range(last):
            return f"OK ({last} in)"
        else:
            return f"OUT OF RANGE ({last} in)"
