# modules/qc_engine/checklist_engine.py

"""
ConcreteOps: QC Engine
Runs standardized and custom quality control checklists for inspection phases before, during, and after pours.
Supports scoring, fail tagging, and audit syncing.
"""

from datetime import datetime
from shared.utils import log_event, trigger_alert


class QCChecklistEngine:
    def __init__(self, pour_id, checklist_name="Generic_QC"):
        self.pour_id = pour_id
        self.checklist_name = checklist_name
        self.results = []
        self.timestamp = datetime.now().isoformat()

    def add_check(self, description: str, passed: bool, note: str = ""):
        check = {
            "description": description,
            "passed": passed,
            "note": note,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(check)
        log_event(f"[{self.pour_id}] QC check: {description} – {'PASS' if passed else 'FAIL'}")

        if not passed:
            trigger_alert(f"[{self.pour_id}] QC FAILURE: {description} – {note}")

    def summary(self):
        total = len(self.results)
        passed = len([r for r in self.results if r["passed"]])
        failed = total - passed
        return {
            "checklist": self.checklist_name,
            "total": total,
            "passed": passed,
            "failed": failed,
            "timestamp": self.timestamp
        }

    def export_json(self):
        return {
            "pour_id": self.pour_id,
            "checklist": self.checklist_name,
            "results": self.results,
            "summary": self.summary()
        }
