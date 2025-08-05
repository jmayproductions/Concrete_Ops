# modules/data_hub/sync_status_checker.py

"""
ConcreteOps: Sync Status Checker
Monitors module-to-pipeline sync status across the ConcreteOps ecosystem.
Verifies latest data pushes, model updates, and config consistency across local and cloud environments.
"""

import os
import datetime
from shared.utils import log_event


class SyncStatusChecker:
    def __init__(self, project_id):
        self.project_id = project_id
        self.last_sync_log = f"S:/Concrete_Ops/logs/{project_id}_last_sync.log"

    def check_sync(self, modules: list) -> dict:
        status_report = {}
        now = datetime.datetime.now()

        for module in modules:
            sync_file = f"S:/Concrete_Ops/modules/{module}/.last_sync"
            if os.path.exists(sync_file):
                with open(sync_file, "r") as f:
                    last_sync = f.read().strip()
                try:
                    last_sync_dt = datetime.datetime.strptime(last_sync, "%Y-%m-%d %H:%M:%S")
                    delta = (now - last_sync_dt).total_seconds() / 3600
                    status_report[module] = f"✅ Last sync: {last_sync_dt} ({delta:.1f} hrs ago)"
                except Exception:
                    status_report[module] = "⚠️ Invalid timestamp format"
            else:
                status_report[module] = "❌ No sync record found"

        self._write_sync_log(status_report)
        return status_report

    def _write_sync_log(self, status_report: dict):
        with open(self.last_sync_log, "w") as f:
            for module, status in status_report.items():
                f.write(f"{module}: {status}\n")
        log_event(f"[{self.project_id}] Sync status log written to {self.last_sync_log}")
