# modules/data_hub/integration_hooks.py

"""
ConcreteOps: Integration Hooks
Provides plug-and-play endpoints to integrate ConcreteOps with external platforms like
Procore, PlanGrid, BIM 360, Bluebeam, Trimble, and others. Enables real-time data exchange and webhook support.
"""

import requests
import json
from shared.utils import log_event


class IntegrationHooks:
    def __init__(self, project_id):
        self.project_id = project_id
        self.supported_platforms = {
            "procore": "https://api.procore.com/vapid/",
            "plangrid": "https://io.plangrid.com/",
            "bim360": "https://developer.api.autodesk.com/",
            "bluebeam": "https://bluebeam.com/api/",
            "trimble": "https://connect.trimble.com/api/"
        }

    def push_update(self, platform: str, endpoint: str, payload: dict, auth_token: str):
        if platform.lower() not in self.supported_platforms:
            raise ValueError(f"{platform} is not currently supported.")

        base_url = self.supported_platforms[platform.lower()]
        full_url = f"{base_url}{endpoint}"

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(full_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            log_event(f"[{self.project_id}] Synced data to {platform} ({endpoint}) — {response.status_code}")
            return response.json()
        except requests.exceptions.RequestException as e:
            log_event(f"[{self.project_id}] Integration error with {platform}: {str(e)}")
            return {"error": str(e)}

    def list_supported(self):
        return list(self.supported_platforms.keys())
