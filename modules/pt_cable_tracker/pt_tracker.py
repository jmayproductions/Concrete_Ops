# modules/pt_cable_manager/pt_tracker.py

"""
ConcreteOps: PT Cable Tracker
Tracks layout, stressing, inspection, and sign-off of post-tension (PT) cables in slab/deck systems.
Ensures compliance, sequence validation, and real-time documentation of stressing operations.
"""

from datetime import datetime
from shared.utils import log_event


class PTCableTracker:
    def __init__(self, project_id):
        self.project_id = project_id
        self.cable_data = {}  # key: cable_id, value: metadata + stress logs

    def register_cable(self, cable_id: str, location: str, planned_stress: int):
        self.cable_data[cable_id] = {
            "location": location,
            "planned_stress_psi": planned_stress,
            "stressing_log": [],
            "inspected": False,
            "certified": False
        }
        log_event(f"[{self.project_id}] PT Cable registered: {cable_id} at {location}")

    def log_stress(self, cable_id: str, actual_psi: int, stressed_by: str):
        if cable_id not in self.cable_data:
            raise ValueError(f"PT Cable {cable_id} not registered.")
        log = {
            "timestamp": datetime.now().isoformat(),
            "psi": actual_psi,
            "technician": stressed_by
        }
        self.cable_data[cable_id]["stressing_log"].append(log)
        log_event(f"[{self.project_id}] Stress logged for {cable_id}: {actual_psi} psi by {stressed_by}")

    def mark_inspected(self, cable_id: str, inspector: str):
        if cable_id in self.cable_data:
            self.cable_data[cable_id]["inspected"] = True
            log_event(f"[{self.project_id}] PT Cable {cable_id} inspected by {inspector}")

    def certify_cable(self, cable_id: str, certifier: str):
        if cable_id in self.cable_data:
            self.cable_data[cable_id]["certified"] = True
            log_event(f"[{self.project_id}] PT Cable {cable_id} certified by {certifier}")

    def get_cable_status(self, cable_id: str):
        return self.cable_data.get(cable_id, None)
