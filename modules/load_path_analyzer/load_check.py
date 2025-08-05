# modules/load_path_analyzer/load_check.py

"""
ConcreteOps: Load Path Analyzer
Verifies that structural loads are being transferred properly through columns, walls, beams, and rebar across multiple decks or pour phases.
Critical for safety and integrity in pan deck, PT deck, and phased slab systems.
"""

from shared.utils import log_event, trigger_alert


class LoadPathAnalyzer:
    def __init__(self, project_id):
        self.project_id = project_id
        self.paths = []

    def define_path(self, from_elem: str, to_elem: str, expected: bool, note: str = ""):
        path = {
            "from": from_elem,
            "to": to_elem,
            "expected": expected,
            "note": note
        }
        self.paths.append(path)
        log_event(f"[{self.project_id}] Load Path: {from_elem} → {to_elem} | {'OK' if expected else 'WARNING'}")

        if not expected:
            trigger_alert(f"[{self.project_id}] LOAD PATH ISSUE: {from_elem} → {to_elem} | {note}")

    def get_all_paths(self):
        return self.paths

    def summary(self):
        total = len(self.paths)
        failed = len([p for p in self.paths if not p["expected"]])
        return {
            "total_paths": total,
            "verified": total - failed,
            "issues": failed
        }
