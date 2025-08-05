# modules/sim_tools/scenario_runner.py

"""
ConcreteOps: Scenario Runner
Simulates concrete pour sequences, weather delays, material flow, and crew productivity to forecast risks,
optimize schedules, and pre-plan mitigation. Allows “what-if” simulations for decision support.
"""

import random
from datetime import datetime
from shared.utils import log_event


class ScenarioRunner:
    def __init__(self, project_id):
        self.project_id = project_id
        self.scenarios = []

    def run_simulation(self, name: str, inputs: dict):
        delay_factor = self._simulate_weather(inputs.get("weather_risk", 0.1))
        crew_eff = self._simulate_crew(inputs.get("crew_variability", 0.15))
        material_risk = self._simulate_material(inputs.get("supply_stability", 0.85))

        total_risk_score = round((delay_factor + crew_eff + material_risk) / 3, 2)

        result = {
            "name": name,
            "timestamp": self._timestamp(),
            "delay_factor": delay_factor,
            "crew_efficiency": crew_eff,
            "material_risk": material_risk,
            "total_risk_score": total_risk_score
        }

        self.scenarios.append(result)
        log_event(f"[{self.project_id}] Scenario '{name}' completed with risk score {total_risk_score}")
        return result

    def _simulate_weather(self, risk_prob):
        return round(random.uniform(0.0, risk_prob), 2)

    def _simulate_crew(self, variability):
        return round(random.uniform(1 - variability, 1 + variability), 2)

    def _simulate_material(self, stability_index):
        return round(1.0 - random.uniform(0, 1 - stability_index), 2)

    def get_all_scenarios(self):
        return self.scenarios

    def _timestamp(self):
        return datetime.now().isoformat()
