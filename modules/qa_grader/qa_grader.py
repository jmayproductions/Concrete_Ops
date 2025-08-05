# modules/qa_grader/qa_grader.py

"""
ConcreteOps: QA Grader Module
Grades concrete test results and determines pass/fail/conditional status based on configured criteria.
"""

from shared.config import STRENGTH_THRESHOLD_PSI
from shared.utils import log_event, trigger_alert


class QAGrader:
    def __init__(self, pour_id):
        self.pour_id = pour_id
        self.results = []

    def ingest_test_result(self, result: dict):
        """
        Accepts a test result in the form:
        {
            "test_type": "compressive_strength",
            "value": 3850,
            "unit": "psi",
            "age_days": 7
        }
        """
        self.results.append(result)
        log_event(f"[{self.pour_id}] Ingested test: {result}")

    def grade(self):
        failures = 0
        conditionals = 0

        for result in self.results:
            if result["test_type"] != "compressive_strength":
                continue

            strength = result["value"]
            if strength >= STRENGTH_THRESHOLD_PSI:
                continue
            elif strength >= STRENGTH_THRESHOLD_PSI * 0.9:
                conditionals += 1
            else:
                failures += 1

        if failures > 0:
            status = "FAIL"
            trigger_alert(f"[{self.pour_id}] QA FAILED with {failures} low breaks.")
        elif conditionals > 0:
            status = "CONDITIONAL"
            trigger_alert(f"[{self.pour_id}] QA CONDITIONAL - borderline results.")
        else:
            status = "PASS"
            log_event(f"[{self.pour_id}] QA PASSED.")

        return {
            "pour_id": self.pour_id,
            "status": status,
            "total_tests": len(self.results),
            "conditionals": conditionals,
            "failures": failures
        }
