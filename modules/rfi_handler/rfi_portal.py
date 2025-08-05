# modules/rfi_handler/rfi_portal.py

"""
ConcreteOps: RFI Portal
Manages Request for Information (RFI) tickets between field crews, GC, engineers, and architects.
Tracks open RFIs, response times, attachments, and links to specific pour phases or locations.
"""

from datetime import datetime
from shared.utils import log_event


class RFIPortal:
    def __init__(self, project_id):
        self.project_id = project_id
        self.rfi_list = {}

    def submit_rfi(self, rfi_id: str, submitted_by: str, subject: str, details: str, pour_id=None):
        self.rfi_list[rfi_id] = {
            "submitted_by": submitted_by,
            "subject": subject,
            "details": details,
            "timestamp": self._timestamp(),
            "status": "open",
            "pour_id": pour_id,
            "responses": []
        }
        log_event(f"[{self.project_id}] New RFI submitted: {rfi_id} — {subject}")

    def respond_to_rfi(self, rfi_id: str, responder: str, message: str):
        if rfi_id not in self.rfi_list:
            raise ValueError(f"RFI {rfi_id} not found.")
        response = {
            "responder": responder,
            "message": message,
            "timestamp": self._timestamp()
        }
        self.rfi_list[rfi_id]["responses"].append(response)
        log_event(f"[{self.project_id}] RFI {rfi_id} responded by {responder}")

    def close_rfi(self, rfi_id: str):
        if rfi_id in self.rfi_list:
            self.rfi_list[rfi_id]["status"] = "closed"
            log_event(f"[{self.project_id}] RFI {rfi_id} marked as closed")

    def get_rfi(self, rfi_id: str):
        return self.rfi_list.get(rfi_id, None)

    def _timestamp(self):
        return datetime.now().isoformat()
