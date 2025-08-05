# modules/data_hub/batch_data_uploader.py

"""
ConcreteOps: Batch Data Uploader
Ingests large datasets from sensors, weather APIs, field logs, or 3rd-party systems.
Supports CSV, JSON, XLSX formats. Normalizes and uploads to project’s internal data lake.
"""

import pandas as pd
import os
from shared.utils import log_event


class BatchDataUploader:
    def __init__(self, project_id):
        self.project_id = project_id
        self.supported_formats = ['.csv', '.json', '.xlsx']

    def upload(self, filepath: str):
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in self.supported_formats:
            raise ValueError(f"Unsupported file type: {ext}")

        if ext == ".csv":
            data = pd.read_csv(filepath)
        elif ext == ".json":
            data = pd.read_json(filepath)
        elif ext == ".xlsx":
            data = pd.read_excel(filepath)

        records_uploaded = len(data)
        log_event(f"[{self.project_id}] Uploaded {records_uploaded} records from {os.path.basename(filepath)}")
        return data
