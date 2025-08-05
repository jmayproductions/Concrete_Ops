# modules/ai_ml/crew_efficiency_analyzer.py

"""
ConcreteOps: Crew Efficiency Analyzer
Evaluates crew performance using time-tracking, task durations, environmental data,
and productivity benchmarks. Flags inefficiencies, fatigue, or misallocated labor.
"""

import numpy as np
import pandas as pd
from shared.utils import log_event


class CrewEfficiencyAnalyzer:
    def __init__(self):
        self.benchmark_rates = {
            "formwork_sqft_hr": 50,
            "rebar_lb_hr": 150,
            "pour_cy_hr": 12,
        }

    def analyze(self, task_data: pd.DataFrame) -> dict:
        """
        task_data: DataFrame with columns:
        ['crew_id', 'task_type', 'start_time', 'end_time', 'quantity', 'weather_temp', 'humidity', 'wind_speed']
        """
        efficiency_report = []

        for _, row in task_data.iterrows():
            task_type = row["task_type"]
            duration_hr = (row["end_time"] - row["start_time"]).total_seconds() / 3600
            actual_rate = row["quantity"] / duration_hr
            benchmark = self.benchmark_rates.get(f"{task_type}_hr", 1)
            efficiency = actual_rate / benchmark

            efficiency_report.append({
                "crew_id": row["crew_id"],
                "task_type": task_type,
                "actual_rate": round(actual_rate, 2),
                "efficiency_ratio": round(efficiency, 2),
                "duration_hr": round(duration_hr, 2),
                "flag": "LOW" if efficiency < 0.75 else "OK"
            })

        df_result = pd.DataFrame(efficiency_report)
        avg_eff = df_result["efficiency_ratio"].mean()

        log_event(f"[CREW-EFFICIENCY] Avg Ratio: {round(avg_eff,2)}")
        return {
            "report": df_result.to_dict(orient="records"),
            "average_efficiency": round(avg_eff, 2),
            "recommendation": "Investigate underperforming crews" if avg_eff < 0.8 else "Performance acceptable"
        }
