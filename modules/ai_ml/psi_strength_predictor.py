# modules/ai_ml/psi_strength_predictor.py

"""
ConcreteOps: PSI Strength Predictor
Uses machine learning regression to forecast 7-day and 28-day compressive strength
based on real-time sensor inputs, mix properties, and ambient conditions.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
from shared.utils import log_event


class PSIStrengthPredictor:
    def __init__(self, model_path="S:/Concrete_Ops/assets/models/psi_strength_model.pkl"):
        self.model = joblib.load(model_path)

    def predict_strength(self, input_data: dict) -> dict:
        """
        input_data = {
            "cement_content": 540,       # lbs/cy
            "w_c_ratio": 0.42,           # Water-Cement Ratio
            "air_content": 5.5,          # Percent
            "curing_temp": 70,           # °F
            "ambient_temp": 68,          # °F
            "humidity": 55,              # Percent
            "days_since_pour": 3         # Current age in days
        }
        """
        input_vector = self._vectorize(input_data)
        predictions = self.model.predict([input_vector])[0]

        result = {
            "predicted_7_day_psi": round(predictions[0], 1),
            "predicted_28_day_psi": round(predictions[1], 1)
        }

        log_event(f"[PSI_PREDICT] 7-day: {result['predicted_7_day_psi']} | 28-day: {result['predicted_28_day_psi']}")
        return result

    def _vectorize(self, data: dict) -> list:
        return [
            data.get("cement_content", 0),
            data.get("w_c_ratio", 0),
            data.get("air_content", 0),
            data.get("curing_temp", 0),
            data.get("ambient_temp", 0),
            data.get("humidity", 0),
            data.get("days_since_pour", 0),
        ]
