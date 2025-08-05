# modules/training_sim/simulation_core.py

"""
ConcreteOps: Training Simulation Core
Interactive sandbox for training field crews, testing logic under edge conditions, and simulating pour day scenarios.
Includes virtual crew behavior, sensor variability, and environmental stress testing.
"""

import random
from shared.utils import log_event


class SimulationCore:
    def __init__(self, project_id):
        self.project_id = project_id
        self.status = "idle"
        self.sim_log = []

    def run_scenario(self, scenario_name, parameters: dict):
        self.status = "running"
        log_event(f"[{self.project_id}] Running simulation: {scenario_name}")
        result = self._simulate_outcome(scenario_name, parameters)
        self.sim_log.append({
            "scenario": scenario_name,
            "parameters": parameters,
            "result": result
        })
        self.status = "idle"
        return result

    def _simulate_outcome(self, scenario_name, parameters):
        # Placeholder logic — customizable by scenario type
        outcome = {
            "success_rate": round(random.uniform(0.6, 1.0), 2),
            "delays_incurred": random.choice(["none", "moderate", "critical"]),
            "crew_efficiency": round(random.uniform(0.7, 1.0), 2),
            "weather_interference": random.choice([True, False])
        }
        log_event(f"[{self.project_id}] Simulation result: {outcome}")
        return outcome

    def get_simulation_log(self):
        return self.sim_log
