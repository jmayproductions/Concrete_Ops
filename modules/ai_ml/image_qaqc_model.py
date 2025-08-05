# modules/ai_ml/image_qaqc_model.py

"""
ConcreteOps: Image QAQC Model
Uses AI-powered computer vision to analyze photos taken during concrete pours and assess quality, compliance,
and potential defects (e.g., honeycombing, cold joints, poor edge finishing).
"""

import torch
import torchvision.transforms as T
from PIL import Image
from shared.utils import log_event

class ImageQAQCModel:
    def __init__(self, model_path="S:/Concrete_Ops/assets/models/cv_qaqc.pt"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = torch.load(model_path, map_location=self.device)
        self.model.eval()
        self.transform = T.Compose([
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def analyze_image(self, image_path: str) -> dict:
        img = Image.open(image_path).convert("RGB")
        input_tensor = self.transform(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)
            predicted_class = torch.argmax(output, dim=1).item()
            confidence = torch.softmax(output, dim=1)[0][predicted_class].item()

        result = {
            "predicted_issue": self._map_class_to_issue(predicted_class),
            "confidence": round(confidence, 4),
            "image_path": image_path
        }

        log_event(f"[QAQC] Analyzed image {image_path} → {result['predicted_issue']} ({confidence:.2%})")
        return result

    def _map_class_to_issue(self, class_idx: int) -> str:
        class_map = {
            0: "No Issues Detected",
            1: "Honeycombing",
            2: "Cold Joint",
            3: "Rebar Misalignment",
            4: "Surface Cracking",
            5: "Poor Edge Finish",
            6: "Void Formation"
        }
        return class_map.get(class_idx, "Unknown")

