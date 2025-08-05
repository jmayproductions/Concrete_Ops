# modules/audit_tools/compliance_engine.py

"""
ConcreteOps: Compliance & Audit Engine
Runs real-time audits on structural compliance against local/national building codes (e.g. ACI, IBC).
Flags non-conformances, auto-generates inspection records, and suggests remediation actions.
"""

from shared.utils import log_event


class ComplianceEngine:
    def __init__(self, project_id):
        self.project_id = project_id
        self.violations = []

    def run_audit(self, inspection_data: dict, code_reference: str = "ACI318-19"):
        results = {
            "code": code_reference,
            "total_checks": 0,
            "violations_found": 0,
            "violations": []
        }

        for check, passed in inspection_data.items():
            results["total_checks"] += 1
            if not passed:
                results["violations_found"] += 1
                results["violations"].append(check)
                self.violations.append({
                    "check": check,
                    "code": code_reference,
                    "timestamp": self._timestamp(),
                })
                log_event(f"[{self.project_id}] CODE VIOLATION: {check} — {code_reference}")

        return results

    def get_all_violations(self):
        return self.violations

    def _timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()
