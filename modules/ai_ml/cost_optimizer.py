# modules/ai_ml/cost_optimizer.py

"""
ConcreteOps: Cost Optimizer
Uses AI to forecast and optimize pour costs, balancing mix specs, logistics,
labor, and equipment against timeline and performance targets.
"""

import numpy as np
from shared.utils import log_event


class CostOptimizer:
    def __init__(self):
        # Placeholder cost weights per unit
        self.cost_weights = {
            "concrete_cy": 135.00,
            "rebar_lb": 0.65,
            "formwork_sqft": 4.50,
            "labor_hr": 60.00,
            "pump_rental_hr": 225.00,
        }

    def evaluate(self, pour_plan: dict) -> dict:
        """
        pour_plan: {
            "volume_cy": 300,
            "rebar_lb": 20000,
            "formwork_sqft": 2500,
            "labor_hr": 180,
            "pump_hr": 12,
            "target_budget": 75000
        }
        """
        raw_cost = (
            pour_plan["volume_cy"] * self.cost_weights["concrete_cy"] +
            pour_plan["rebar_lb"] * self.cost_weights["rebar_lb"] +
            pour_plan["formwork_sqft"] * self.cost_weights["formwork_sqft"] +
            pour_plan["labor_hr"] * self.cost_weights["labor_hr"] +
            pour_plan["pump_hr"] * self.cost_weights["pump_rental_hr"]
        )

        delta = pour_plan["target_budget"] - raw_cost
        status = "UNDER BUDGET" if delta >= 0 else "OVER BUDGET"

        log_event(f"[COST] Total: ${raw_cost:,.2f} | {status} by ${abs(delta):,.2f}")

        return {
            "total_cost": round(raw_cost, 2),
            "budget_difference": round(delta, 2),
            "status": status
        }

    def adjust_mix_design(self, mix_options: list, strength_target: int) -> dict:
        """
        Simulate value-engineering different mixes to hit psi & cost targets.
        mix_options: list of dicts with mix properties and unit cost
        """
        viable = [mix for mix in mix_options if mix["predicted_psi"] >= strength_target]
        best = min(viable, key=lambda x: x["unit_cost"]) if viable else None

        if best:
            log_event(f"[MIX_OPT] Selected mix: {best['name']} (${best['unit_cost']}/cy)")
            return best
        else:
            log_event("[MIX_OPT] No viable mix found!")
            return {"error": "No mixes meet strength target"}
