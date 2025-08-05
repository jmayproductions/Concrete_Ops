# modules/qaqc_engine/checklist_engine.py

"""
ConcreteOps: QAQC Engine – Checklist Engine
Dynamically generates and validates field checklists by zone and activity (e.g., rebar, embeds, PT, pre-pour, post-pour).
Supports scoring, failure tracking, resolution chaining, and reporting.
"""

from datetime import datetime
from shared.utils import log_event


class QAQCEngine:
    def __init__(self, zone_id):
        self.zone_id = zone_id
        self.checklists = {}

    def create_checklist(self, checklist_name, items: list):
        self.checklists[checklist_name] = {
            "created_at": datetime.now().isoformat(),
            "items": {item: {"status": "pending", "notes": ""} for item in items}
        }
        log_event(f"[{self.zone_id}] QAQC checklist created: {checklist_name}")

    def mark_item(self, checklist_name, item, status, notes=""):
        if checklist_name in self.checklists and item in self.checklists[checklist_name]["items"]:
            self.checklists[checklist_name]["items"][item] = {
                "status": status,
                "notes": notes
            }
            log_event(f"[{self.zone_id}] {item} marked as {status} ({checklist_name})")

    def get_checklist_status(self, checklist_name):
        checklist = self.checklists.get(checklist_name)
        if not checklist:
            return None
        counts = {"passed": 0, "failed": 0, "pending": 0}
        for item_data in checklist["items"].values():
            counts[item_data["status"]] += 1
        return counts

    def get_failed_items(self):
        failed = {}
        for name, cl in self.checklists.items():
            failed_items = [i for i, d in cl["items"].items() if d["status"] == "failed"]
            if failed_items:
                failed[name] = failed_items
        return failed
