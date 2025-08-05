# modules/ai_ml/thermal_crack_predictor.py

"""
ConcreteOps: Thermal Crack Predictor
Uses machine learning to detect risk of early-stage thermal cracking in structural pours,
based on curing temperature curves, ambient weather data, and mix design parameters.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
from shared.utils import log_event


class ThermalCrackPredictor:
    def __init__(self, model_path="S:/Concrete_Ops/assets/models/thermal_crack_rf.pkl"):
        self.model = joblib.load(model_path)

    def assess_crack_risk(self, data: dict) -> dict:
        input_vector = self._prepare_input(data)
        prediction = self.model.predict([input_vector])[0]
        probability = self.model.predict_proba([input_vector])[0]

        result = {
            "risk_level": self._map_prediction(prediction),
            "confidence": round(float(np.max(probability)), 4),
            "raw_probs": probability.tolist()
        }

        log_event(f"[THERMAL_CRACK] Risk={result['risk_level']} | Conf={result['confidence']}")
        return result

    def _prepare_input(self, data: dict) -> list:
        return [
            data.get("initial_temp", 0),        # °F
            data.get("max_temp", 0),            # °F
            data.get("delta_temp", 0),          # °F
            data.get("ambient_temp", 0),        # °F
            data.get("humidity", 0),            # %
            data.get("wind_speed", 0),          # mph
            data.get("cement_content", 0),      # lbs/cy
            data.get("water_cement_ratio", 0),  # ratio
            data.get("slab_thickness", 0),      # inches
            data.get("curing_days", 0),         # days
        ]

    def _map_prediction(self, label: int) -> str:
        return {
            0: "Low Risk",
            1: "Moderate Risk",
            2: "High Risk"
        }.get(label, "Unknown")
