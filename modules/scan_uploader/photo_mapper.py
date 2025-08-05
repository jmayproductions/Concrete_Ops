# modules/scan_uploader/photo_mapper.py

"""
ConcreteOps: Field Photo Mapper
Uploads and maps field photos to zone IDs or coordinates for visual QA, incident review, or layout verification.
Supports cross-referencing with checklists, timestamps, and location tags.
"""

import os
from datetime import datetime
from shared.utils import log_event


class PhotoMapper:
    def __init__(self, pour_id, save_dir="data/field_photos"):
        self.pour_id = pour_id
        self.save_dir = os.path.join(save_dir, pour_id)
        os.makedirs(self.save_dir, exist_ok=True)
        self.manifest = []

    def tag_and_save(self, image_bytes, zone_id: str, description: str = ""):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{zone_id}_{timestamp}.jpg"
        path = os.path.join(self.save_dir, filename)

        with open(path, "wb") as f:
            f.write(image_bytes)

        entry = {
            "zone_id": zone_id,
            "description": description,
            "timestamp": timestamp,
            "filename": filename,
            "path": path
        }
        self.manifest.append(entry)
        log_event(f"[{self.pour_id}] Photo saved: {filename} @ zone {zone_id}")

    def get_manifest(self):
        return self.manifest
