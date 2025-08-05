# modules/integration_router/router.py

"""
ConcreteOps: Integration Router
Central routing layer for module communication and orchestration.
Acts as the middleware brain—connecting sensor input, crew logs, QAQC, forecasts, material ETAs, and external APIs.
"""

from shared.utils import log_event

# Example imports (expand with actual module hooks as needed)
# from modules.weather_integration.weather_monitor import WeatherMonitor
# from modules.pour_manager.pour_tracker import PourTracker
# from modules.mix_design_validator.mix_checker import MixChecker
# from modules.ai_insight.forecast_bot import ForecastBot

class IntegrationRouter:
    def __init__(self, project_id):
        self.project_id = project_id
        self.active_modules = {}

    def register_module(self, name, module_ref):
        self.active_modules[name] = module_ref
        log_event(f"[{self.project_id}] Module registered: {name}")

    def broadcast(self, event_type: str, data: dict):
        log_event(f"[{self.project_id}] Broadcasting {event_type} with payload: {data}")
        for name, module in self.active_modules.items():
            if hasattr(module, "on_event"):
                module.on_event(event_type, data)

    def get_registered_modules(self):
        return list(self.active_modules.keys())

    def route_event_to(self, module_name: str, event_type: str, data: dict):
        module = self.active_modules.get(module_name)
        if module and hasattr(module, "on_event"):
            log_event(f"[{self.project_id}] Routing {event_type} to {module_name}")
            module.on_event(event_type, data)
        else:
            log_event(f"[{self.project_id}] Module {module_name} cannot receive events or not found.")
