# modules/decision_log_writer/log_writer.py

"""
ConcreteOps: Decision Log Writer
Creates an auditable log of decisions, anomalies, overrides, approvals, and field resolutions — critical for liability, compliance, and transparency.
"""

from datetime import datetime
from shared.utils import log_event


class DecisionLogWriter:
    def __init__(self, pour_id):
        self.pour_id = pour_id
        self.decision_log = []

    def record_decision(self, actor: str, action: str, reason: str, override: bool = False):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "actor": actor,
            "action": action,
            "reason": reason,
            "override": override
        }
        self.decision_log.append(entry)
        status = "OVERRIDE" if override else "LOG"
        log_event(f"[{self.pour_id}] [{status}] {actor}: {action} – {reason}")

    def get_full_log(self):
        return self.decision_log

    def export_log(self, filepath: str):
        with open(filepath, "w") as f:
            for entry in self.decision_log:
                f.write(f"{entry['timestamp']} | {entry['actor']} | {entry['action']} | {entry['reason']} | OVERRIDE={entry['override']}\n")
