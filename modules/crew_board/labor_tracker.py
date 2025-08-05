# modules/crew_board/labor_tracker.py

"""
ConcreteOps: Crew Board – Labor Tracker
Monitors daily crew assignments, roles, clock-ins, and task progress for labor tracking, payroll reporting, and productivity analysis.
"""

from datetime import datetime
from shared.utils import log_event


class LaborTracker:
    def __init__(self, project_id):
        self.project_id = project_id
        self.log = []

    def check_in(self, worker_id: str, role: str, task: str):
        entry = {
            "worker_id": worker_id,
            "role": role,
            "task": task,
            "check_in": datetime.now().isoformat(),
            "check_out": None,
            "status": "in"
        }
        self.log.append(entry)
        log_event(f"[{self.project_id}] {worker_id} checked in as {role} – Task: {task}")

    def check_out(self, worker_id: str):
        for entry in self.log:
            if entry["worker_id"] == worker_id and entry["status"] == "in":
                entry["check_out"] = datetime.now().isoformat()
                entry["status"] = "out"
                log_event(f"[{self.project_id}] {worker_id} checked out")
                break

    def get_active_workers(self):
        return [e for e in self.log if e["status"] == "in"]

    def daily_report(self):
        return {
            "project": self.project_id,
            "entries": self.log,
            "total_workers": len(set(e["worker_id"] for e in self.log))
        }
