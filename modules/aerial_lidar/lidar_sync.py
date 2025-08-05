# modules/aerial_lidar/lidar_sync.py

"""
ConcreteOps: Aerial Lidar Sync Engine
Integrates Lidar scans from drone or tripod to validate site elevation, edge condition, slope,
and deck prep accuracy. Syncs with BIM model and flags variance from tolerance thresholds.
"""

import numpy as np
from shared.utils import log_event


class LidarSync:
    def __init__(self, project_id):
        self.project_id = project_id
        self.tolerance_mm = 5.0  # default max elevation deviation in mm

    def analyze_lidar_data(self, lidar_points: np.ndarray, bim_surface: np.ndarray):
        """
        Compares raw lidar point cloud (XYZ) to BIM surface (XYZ).
        Returns out-of-spec locations for field correction.
        """
        if lidar_points.shape != bim_surface.shape:
            raise ValueError("Lidar and BIM surfaces must have same shape.")

        deviations = np.abs(lidar_points[:, 2] - bim_surface[:, 2])
        violations = np.where(deviations > self.tolerance_mm)[0]
        flagged_points = lidar_points[violations]

        log_event(f"[{self.project_id}] Lidar analysis complete: {len(flagged_points)} points out of spec.")
        return flagged_points.tolist()

    def set_tolerance(self, new_tolerance_mm: float):
        self.tolerance_mm = new_tolerance_mm
        log_event(f"[{self.project_id}] Elevation tolerance set to {new_tolerance_mm}mm")
