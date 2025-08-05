# modules/ai_ml/predictive_strength_model.py

"""
ConcreteOps: Predictive Strength Model
Uses machine learning to forecast concrete strength gain curves based on mix design,
weather, placement method, and curing conditions. Assists with early formwork removal and PT tensioning decisions.
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from shared.utils import log_event


class PredictiveStrengthModel:
    def __init__(self, project_id):
        self.project_id = project_id
        self.model = RandomForestRegressor(n_estimators=100)
        self.trained = False

    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        self.model.fit(X_train, y_train)
        self.trained = True
        log_event(f"[{self.project_id}] Strength prediction model trained with {len(X_train)} samples.")

    def predict_strength(self, input_features: np.ndarray) -> float:
        if not self.trained:
            raise RuntimeError("Model must be trained before predictions can be made.")
        prediction = self.model.predict([input_features])[0]
        log_event(f"[{self.project_id}] Predicted strength: {round(prediction, 2)} MPa")
        return round(prediction, 2)

    def explain_model(self):
        """
        Returns relative feature importance for interpretability.
        """
        if not self.trained:
            return {}
        importances = self.model.feature_importances_
        return dict(enumerate(importances))
