# modules/ai_ml/labor_forecast_model.py

"""
ConcreteOps: Labor Forecast Model
Uses machine learning to predict labor demand per pour phase based on scope, complexity,
weather, layout, and crew performance history. Helps optimize manpower, reduce overtime, and balance shift loads.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from shared.utils import log_event


class LaborForecastModel:
    def __init__(self, project_id):
        self.project_id = project_id
        self.model = LinearRegression()
        self.trained = False

    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        self.model.fit(X_train, y_train)
        self.trained = True
        log_event(f"[{self.project_id}] Labor forecast model trained with {len(X_train)} samples.")

    def predict_labor_hours(self, input_features: np.ndarray) -> float:
        if not self.trained:
            raise RuntimeError("Model must be trained before making predictions.")
        prediction = self.model.predict([input_features])[0]
        log_event(f"[{self.project_id}] Forecasted labor: {round(prediction, 1)} hours")
        return round(prediction, 1)

    def get_coefficients(self):
        """
        Returns model coefficients for feature impact review.
        """
        if not self.trained:
            return {}
        return dict(enumerate(self.model.coef_))
