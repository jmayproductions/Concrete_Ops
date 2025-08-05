# modules/report_packer/generate_report.py

"""
ConcreteOps: Report Packer
Generates a human-readable report from pour data, test results, QA grading, and metadata for archival and export.
"""

import json
import os
from datetime import datetime
from shared.config import REPORT_METADATA
from shared.utils import log_event


class ReportPacker:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, pour_id, qa_result, telemetry_log, override_log, violations=[]):
        """
        Assemble the full QA report and write to disk as JSON.
        """
        report = {
            "pour_id": pour_id,
            "generated_at": datetime.now().isoformat(),
            "status": qa_result.get("status", "UNKNOWN"),
            "qa_result": qa_result,
            "telemetry_log": telemetry_log,
            "override_log": override_log,
            "violations": violations,
            "meta": REPORT_METADATA,
        }

        filename = f"{pour_id}_qa_report.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w") as f:
            json.dump(report, f, indent=4)

        log_event(f"[{pour_id}] QA report generated at {filepath}")
        return filepath
