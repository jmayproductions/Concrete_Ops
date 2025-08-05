# modules/safety_tracker/incident_logger.py

"""
ConcreteOps: Safety Tracker – Incident Logger
Captures and logs jobsite safety incidents, hazards, and near misses. Tracks root cause, resolution, severity, and logs time/location for audit and reporting.
"""

from datetime import datetime
from shared.utils import log_event, trigger_alert


class SafetyIncidentLogger:
    def __init__(self, project_id):
        self.project_id = project_id
        self.incidents = []

    def log_incident(self, category: str, description: str, zone: str, severity: str, resolved: bool = False):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,  # e.g., “trip hazard”, “electrical”, “fall protection”
            "description": description,
            "zone": zone,
            "severity": severity,  # e.g., “low”, “medium”, “high”, “fatal”
            "resolved": resolved
        }
        self.incidents.append(entry)

        log_event(f"[{self.project_id}] SAFETY INCIDENT in {zone}: {description} | Severity: {severity}")

        if severity.lower() in ["high", "fatal"] and not resolved:
            trigger_alert(f"⚠️ URGENT SAFETY INCIDENT in {zone} – {description}")

    def get_unresolved(self):
        return [i for i in self.incidents if not i["resolved"]]

    def export_report(self):
        return {
            "project_id": self.project_id,
            "total_incidents": len(self.incidents),
            "open_cases": len(self.get_unresolved()),
            "log": self.incidents
        }
