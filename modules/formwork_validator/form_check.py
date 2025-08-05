# modules/formwork_validator/form_check.py

"""
ConcreteOps: Formwork Validator
Validates form layout, plumb, level, square, and bracing using manual input or automated scan/photo integrations.
Critical for preventing pour blowouts, dimensional errors, and layout mistakes.
"""

from shared.utils import log_event, trigger_alert
from shared.config import FORMWORK_TOLERANCES


class FormworkValidator:
    def __init__(self, pour_id):
        self.pour_id = pour_id
        self.form_checks = []

    def add_check(self, point_id: str, plumb_ok: bool, level_ok: bool, braced_ok: bool):
        passed = all([plumb_ok, level_ok, braced_ok])
        check = {
            "point": point_id,
            "plumb": plumb_ok,
            "level": level_ok,
            "braced": braced_ok,
            "passed": passed
        }
        self.form_checks.append(check)

        status = "PASS" if passed else "FAIL"
        log_event(f"[{self.pour_id}] Form Check {point_id}: {status}")

        if not passed:
            trigger_alert(f"[{self.pour_id}] FORM FAILURE at {point_id}")

    def summary(self):
        total = len(self.form_checks)
        failed = len([c for c in self.form_checks if not c["passed"]])
        return {
            "total_points": total,
            "failures": failed,
            "passed": total - failed
        }
