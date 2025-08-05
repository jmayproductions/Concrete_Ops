# modules/ai_ml/strength_prediction_ann.py

"""
ConcreteOps: Strength Prediction ANN
Artificial Neural Network (ANN) model to estimate 7-day and 28-day compressive strength (PSI) of concrete,
based on input variables like mix design, ambient conditions, curing data, and placement method.
"""

import torch
import torch.nn as nn
import numpy as np
from shared.utils import log_event


class StrengthANN(nn.Module):
    def __init__(self, input_size=8, hidden_size=32, output_size=2):
        super(StrengthANN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        return self.fc2(out)


class StrengthPredictor:
    def __init__(self, model_path="S:/Concrete_Ops/assets/models/psi_ann_model.pt"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = StrengthANN().to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

    def predict(self, features: dict) -> dict:
        input_vector = self._prepare_input(features)
        with torch.no_grad():
            tensor_input = torch.tensor(input_vector, dtype=torch.float32).to(self.device)
            prediction = self.model(tensor_input)
            psi_7_day, psi_28_day = prediction.cpu().numpy()

        log_event(f"[STRENGTH-ANN] PSI Prediction: 7-Day={psi_7_day:.0f}, 28-Day={psi_28_day:.0f}")
        return {
            "psi_7_day": round(psi_7_day, 2),
            "psi_28_day": round(psi_28_day, 2)
        }

    def _prepare_input(self, features: dict) -> list:
        return [
            features.get("cement_content", 0),
            features.get("water_cement_ratio", 0),
            features.get("ambient_temp", 0),
            features.get("humidity", 0),
            features.get("curing_days", 0),
            features.get("mix_slump", 0),
            features.get("admixtures", 0),
            features.get("pour_method", 0),
        ]
