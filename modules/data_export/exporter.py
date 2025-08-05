# modules/data_export/exporter.py

"""
ConcreteOps: Data Exporter
Exports structured project data, pour logs, QAQC results, safety incidents, forecasts, and material usage into JSON, CSV, and PDF-ready formats.
Supports archiving, compliance reporting, and external system handoffs.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from shared.utils import log_event


class DataExporter:
    def __init__(self, project_id, export_dir="exports"):
        self.project_id = project_id
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_json(self, data, filename: str):
        path = self.export_dir / f"{self.project_id}_{filename}.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        log_event(f"[{self.project_id}] JSON export saved: {path}")

    def export_csv(self, data: list, filename: str):
        path = self.export_dir / f"{self.project_id}_{filename}.csv"
        if data and isinstance(data, list) and isinstance(data[0], dict):
            keys = data[0].keys()
            with open(path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            log_event(f"[{self.project_id}] CSV export saved: {path}")
        else:
            log_event(f"[{self.project_id}] Invalid data format for CSV export.")

    def export_txt_snapshot(self, summary: str, filename: str = None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        fname = filename or f"snapshot_{timestamp}.txt"
        path = self.export_dir / f"{self.project_id}_{fname}"
        with open(path, "w") as f:
            f.write(summary)
        log_event(f"[{self.project_id}] Snapshot text export saved: {path}")
