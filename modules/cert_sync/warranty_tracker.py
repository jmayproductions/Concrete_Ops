# modules/cert_sync/warranty_tracker.py

"""
ConcreteOps: Warranty & Certification Tracker
Maintains records of warranties, certifications, and lifecycle data for all materials and systems used
in each concrete pour phase. Ensures traceability, accountability, and handoff readiness.
"""

from datetime import datetime
from shared.utils import log_event


class WarrantyTracker:
    def __init__(self, project_id):
        self.project_id = project_id
        self.asset_registry = {}

    def register_asset(self, asset_id: str, description: str, supplier: str, warranty_period_months: int):
        self.asset_registry[asset_id] = {
            "description": description,
            "supplier": supplier,
            "warranty_months": warranty_period_months,
            "install_date": self._timestamp(),
            "certs": [],
            "notes": []
        }
        log_event(f"[{self.project_id}] Asset registered: {asset_id} from {supplier}")

    def add_certification(self, asset_id: str, cert_name: str, issued_by: str):
        if asset_id not in self.asset_registry:
            raise ValueError(f"Asset {asset_id} not found.")
        self.asset_registry[asset_id]["certs"].append({
            "name": cert_name,
            "issued_by": issued_by,
            "timestamp": self._timestamp()
        })
        log_event(f"[{self.project_id}] Certification added: {cert_name} for {asset_id}")

    def add_note(self, asset_id: str, note: str):
        if asset_id in self.asset_registry:
            self.asset_registry[asset_id]["notes"].append({
                "note": note,
                "timestamp": self._timestamp()
            })

    def get_asset_record(self, asset_id: str):
        return self.asset_registry.get(asset_id, None)

    def _timestamp(self):
        return datetime.now().isoformat()
