# modules/crew_input_logger/input_recorder.py

"""
ConcreteOps: Crew Input Logger
Captures manual field input, overrides, and observations from foremen or inspectors during active pour operations.
"""

from datetime import datetime
from shared.utils import log_event


class InputRecorder:
    def __init__(self, pour_id):
        self.pour_id = pour_id
        self.entries = []

    def record(self, author: str, message: str, critical: bool = False):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "author": author,
            "message": message,
            "critical": critical
        }
        self.entries.append(entry)
        log_event(f"[{self.pour_id}] Crew input logged: {entry}")

        if critical:
            from shared.utils import trigger_alert
            trigger_alert(f"[{self.pour_id}] Critical field input: {message}")

    def get_log(self):
        return self.entries

    def export_to_dict(self):
        return {
            "pour_id": self.pour_id,
            "inputs": self.entries
        }
