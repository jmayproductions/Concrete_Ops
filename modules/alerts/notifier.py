# modules/alerts/notifier.py

"""
ConcreteOps: Alert Notifier
Unified alerting system for pushing critical messages to field crew, dashboard, supervisors, or integrations (email, SMS, radio, Teams/Slack).
Supports real-time alerts from QAQC, weather, forecast engine, and curing sensors.
"""

from datetime import datetime
from shared.utils import log_event


class Notifier:
    def __init__(self, project_id):
        self.project_id = project_id
        self.alert_log = []

    def send_alert(self, level: str, message: str, module_source: str = "system"):
        alert = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),  # e.g., INFO, WARNING, CRITICAL
            "message": message,
            "source": module_source
        }
        self.alert_log.append(alert)
        log_event(f"[{self.project_id}] [{level.upper()}] {module_source}: {message}")
        self.push_to_dashboard(alert)

    def push_to_dashboard(self, alert):
        # Placeholder — would send to UI, API, or log store
        print(f"[ALERT - {alert['level']}] {alert['message']}")

    def get_alert_history(self, filter_level=None):
        if filter_level:
            return [a for a in self.alert_log if a["level"] == filter_level.upper()]
        return self.alert_log
