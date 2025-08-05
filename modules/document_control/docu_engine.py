# modules/document_control/docu_engine.py

"""
ConcreteOps: Document Control Engine
Handles structured intake, storage, and versioning of key project documents:
drawings, RFIs, submittals, as-builts, safety sheets, and inspection records.
Ensures traceability and linkage to related pour events.
"""

from datetime import datetime
from pathlib import Path
from shared.utils import log_event


class DocumentEngine:
    def __init__(self, project_id, storage_root="documents"):
        self.project_id = project_id
        self.storage_path = Path(storage_root) / project_id
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def store_document(self, doc_type: str, filename: str, content: bytes):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        doc_dir = self.storage_path / doc_type
        doc_dir.mkdir(exist_ok=True)
        final_path = doc_dir / f"{timestamp}_{filename}"
        with open(final_path, "wb") as f:
            f.write(content)
        log_event(f"[{self.project_id}] Document stored: {final_path}")
        return final_path

    def list_documents(self, doc_type: str = None):
        target_dir = self.storage_path if not doc_type else self.storage_path / doc_type
        if not target_dir.exists():
            return []
        return [str(p) for p in target_dir.glob("*") if p.is_file()]
