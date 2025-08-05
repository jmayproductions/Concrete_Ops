# modules/data_hub/data_cleanser.py

"""
ConcreteOps: Data Cleanser & Schema Validator
Cleans, normalizes, and validates incoming datasets. Auto-fixes common formatting issues and ensures compliance
with internal schema standards. Prevents downstream failures in analytics, ML, and reporting.
"""

import pandas as pd
from shared.utils import log_event


class DataCleanser:
    def __init__(self, project_id):
        self.project_id = project_id
        self.required_columns = {
            "timestamp": "datetime64[ns]",
            "location": "str",
            "sensor_id": "str",
            "reading": "float"
        }

    def cleanse(self, df: pd.DataFrame) -> pd.DataFrame:
        log_event(f"[{self.project_id}] Starting data cleansing on {len(df)} rows")

        # Standardize column names
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Fill missing required fields
        for col, dtype in self.required_columns.items():
            if col not in df.columns:
                df[col] = pd.NA

        # Convert types
        for col, dtype in self.required_columns.items():
            try:
                df[col] = df[col].astype(dtype)
            except Exception:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop completely empty rows
        df.dropna(how="all", inplace=True)

        log_event(f"[{self.project_id}] Cleaned data ready with {len(df)} valid rows")
        return df

    def validate_schema(self, df: pd.DataFrame) -> bool:
        missing = [col for col in self.required_columns if col not in df.columns]
        if missing:
            log_event(f"[{self.project_id}] Schema validation failed. Missing: {missing}")
            return False
        log_event(f"[{self.project_id}] Schema validation passed.")
        return True
