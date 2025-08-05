# modules/pour_manager/pour_manager.py

"""
ConcreteOps: Pour Manager Module
Handles the full lifecycle of a concrete pour from scheduling, pre-checks, execution, and post-pour logging.
"""

from datetime import datetime
from shared.config import POUR_TIME_WINDOW
from shared.utils import log_event, trigger_alert
from logic.scheduler import is_within_window
from logic.validator import validate_mix_design, validate_site_conditions


class PourManager:
    def __init__(self, pour_id, mix, crew_profile, site_conditions):
        self.pour_id = pour_id
        self.mix = mix
        self.crew = crew_profile
        self.conditions = site_conditions
        self.status = "initialized"
        self.start_time = None
        self.end_time = None

    def precheck(self):
        """Run pre-pour validation logic before triggering pour"""
        if not is_within_window(POUR_TIME_WINDOW):
            trigger_alert("Pour window violation")
            return False
        if not validate_mix_design(self.mix):
            trigger_alert("Invalid mix design")
            return False
        if not validate_site_conditions(self.conditions):
            trigger_alert("Unsafe site conditions")
            return False
        log_event(f"[{self.pour_id}] Precheck PASSED")
        return True

    def begin_pour(self):
        if self.precheck():
            self.start_time = datetime.now()
            self.status = "pouring"
            log_event(f"[{self.pour_id}] Pour started at {self.start_time}")
        else:
            self.status = "blocked"
            log_event(f"[{self.pour_id}] Pour BLOCKED by precheck")

    def end_pour(self):
        if self.status != "pouring":
            log_event(f"[{self.pour_id}] Cannot end pour: status = {self.status}")
            return
        self.end_time = datetime.now()
        self.status = "completed"
        log_event(f"[{self.pour_id}] Pour completed at {self.end_time}")

    def get_status(self):
        return {
            "pour_id": self.pour_id,
            "status": self.status,
            "started": self.start_time,
            "ended": self.end_time,
        }
