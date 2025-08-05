# modules/fail_safe_engine/failsafe_core.py

"""
ConcreteOps: Fail-Safe Engine Core
Executes enforcement of critical operational rules, halts pours, and triggers alerts when thresholds or logic constraints are violated.
"""

from shared.utils import log_event, trigger_alert
from shared.config import FAILSAFE_RULES


class FailSafeEngine:
    def __init__(self, pour_id):
        self.pour_id = pour_id
        self.violations = []

    def evaluate(self, telemetry: dict, site_conditions: dict):
        """
        Checks current telemetry and conditions against all registered fail-safe rules.

        telemetry = {
            "slump": 5.5,
            "temperature": 92,
            "humidity": 30,
            "strength_estimate": 3100
        }

        site_conditions = {
            "wind_speed": 15,
            "evaporation_rate": 0.28
        }
        """
        for rule in FAILSAFE_RULES:
            metric = rule["metric"]
            comparator = rule["comparator"]
            threshold = rule["threshold"]

            source = telemetry if metric in telemetry else site_conditions
            if metric not in source:
                continue  # skip unknown metrics

            value = source[metric]
            if not self._compare(value, comparator, threshold):
                self.violations.append({
                    "metric": metric,
                    "value": value,
                    "threshold": threshold,
                    "comparator": comparator
                })
                trigger_alert(f"[{self.pour_id}] Fail-safe violation: {metric} = {value} ({comparator} {threshold})")

        if self.violations:
            log_event(f"[{self.pour_id}] FAIL-SAFE BLOCKED pour with {len(self.violations)} violations.")
            return False
        return True

    def _compare(self, value, comparator, threshold):
        if comparator == ">": return value > threshold
        if comparator == ">=": return value >= threshold
        if comparator == "<": return value < threshold
        if comparator == "<=": return value <= threshold
        if comparator == "==": return value == threshold
        return False

    def get_violations(self):
        return self.violations
