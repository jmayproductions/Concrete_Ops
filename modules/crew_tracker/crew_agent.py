# modules/crew_tracker/crew_agent.py

"""
ConcreteOps: Crew Agent
Tracks manpower, crew composition, clock-in/clock-out, and field anomalies tied to productivity or safety deviations.
"""

from datetime import datetime
from shared.utils import log_event


class CrewAgent:
    def __init__(self, pour_id):
        self.pour_id = pour_id
        self.crew_log = []

    def clock_in(self, name: str, role: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "role": role,
            "status": "IN"
        }
        self.crew_log.append(entry)
        log_event(f"[{self.pour_id}] Crew IN: {name} ({role})")

    def clock_out(self, name: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "status": "OUT"
        }
        self.crew_log.append(entry)
        log_event(f"[{self.pour_id}] Crew OUT: {name}")

    def report_issue(self, name: str, note: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "status": "ISSUE",
            "note": note
        }
        self.crew_log.append(entry)
        log_event(f"[{self.pour_id}] Crew ISSUE: {name} – {note}")

    def get_crew_summary(self):
        in_count = len([e for e in self.crew_log if e["status"] == "IN"])
        out_count = len([e for e in self.crew_log if e["status"] == "OUT"])
        return {"clocked_in": in_count, "clocked_out": out_count}
