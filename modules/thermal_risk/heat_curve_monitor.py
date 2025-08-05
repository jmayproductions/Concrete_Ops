# modules/thermal_risk/heat_curve_monitor.py

"""
ConcreteOps: Heat Curve Monitor
Analyzes temperature differential within a slab or mass pour to predict thermal cracking risk and trigger insulation or schedule changes.
"""

from shared.utils import log_event, trigger_alert
from shared.config import THERMAL_LIMITS


class HeatCurveMonitor:
    def __init__(self, pour_id):
        self.pour_id = pour_id
        self.internal_temps = []
        self.surface_temps = []

    def record(self, core_temp: float, surface_temp: float):
        self.internal_temps.append(core_temp)
        self.surface_temps.append(surface_temp)
        log_event(f"[{self.pour_id}] Heat curve: Core={core_temp}°F, Surface={surface_temp}°F")

        diff = abs(core_temp - surface_temp)
        if diff > THERMAL_LIMITS["max_diff"]:
            trigger_alert(f"[{self.pour_id}] Thermal cracking risk: ΔT = {diff}°F")

    def get_latest_delta(self):
        if not self.internal_temps or not self.surface_temps:
            return None
        return abs(self.internal_temps[-1] - self.surface_temps[-1])
