# modules/material_optimizer/mix_calc.py

"""
ConcreteOps: Mix Calculator
Calculates concrete volume requirements per zone, accounts for waste factors, and suggests optimal truck orders based on pour size and mix type.
"""

from shared.utils import log_event
from math import ceil


class MixCalculator:
    def __init__(self, project_id):
        self.project_id = project_id
        self.records = []

    def calculate_volume(self, length_ft, width_ft, depth_in):
        cubic_yds = (length_ft * width_ft * (depth_in / 12)) / 27
        return round(cubic_yds, 2)

    def estimate_mix(self, zone_id: str, length_ft: float, width_ft: float, depth_in: float, mix_type: str, waste_factor=0.1):
        base_vol = self.calculate_volume(length_ft, width_ft, depth_in)
        total_vol = round(base_vol * (1 + waste_factor), 2)
        trucks_needed = ceil(total_vol / 10)  # Assuming 10 CY per truck

        mix_plan = {
            "zone_id": zone_id,
            "length_ft": length_ft,
            "width_ft": width_ft,
            "depth_in": depth_in,
            "mix_type": mix_type,
            "base_volume_cy": base_vol,
            "total_with_waste": total_vol,
            "truck_count": trucks_needed
        }

        self.records.append(mix_plan)
        log_event(f"[{self.project_id}] Mix plan for {zone_id}: {total_vol} CY, {trucks_needed} trucks")
        return mix_plan

    def get_all_mix_plans(self):
        return self.records
