# modules/devops_integration/api_adapter.py

"""
ConcreteOps: DevOps Integration – API Adapter
Provides adapter functions for connecting ConcreteOps to external platforms such as Procore, PlanGrid, Bluebeam, Revit, or custom REST APIs.
Used for syncing schedules, drawings, material orders, field data, and more.
"""

import requests
from shared.utils import log_event


class APIAdapter:
    def __init__(self, system_name, base_url, auth_token):
        self.system_name = system_name
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token

    def send_post(self, endpoint, payload):
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        log_event(f"[{self.system_name}] POST {endpoint} | Status: {response.status_code}")
        return response.json()

    def fetch_get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }

        response = requests.get(url, headers=headers, params=params)
        log_event(f"[{self.system_name}] GET {endpoint} | Status: {response.status_code}")
        return response.json()
