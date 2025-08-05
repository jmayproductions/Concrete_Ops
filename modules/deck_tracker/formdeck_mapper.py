# modules/deck_tracker/formdeck_mapper.py

"""
ConcreteOps: Form Deck Mapper
Tracks and verifies form deck layouts for suspended slab systems (pan deck, corrugated metal, plywood),
validates shoring/reshoring layout, and maps pour sequences for safety and QC.
"""

from shared.utils import log_event


class FormDeckMapper:
    def __init__(self, project_id):
        self.project_id = project_id
        self.deck_zones = {}

    def register_zone(self, zone_id: str, layout_type: str, supports_verified: bool = False):
        self.deck_zones[zone_id] = {
            "layout_type": layout_type,
            "supports_verified": supports_verified,
            "inspections": [],
            "pour_status": "pending"
        }
        log_event(f"[{self.project_id}] Deck zone registered: {zone_id} ({layout_type})")

    def mark_supports_verified(self, zone_id: str, inspector: str):
        if zone_id in self.deck_zones:
            self.deck_zones[zone_id]["supports_verified"] = True
            self.deck_zones[zone_id]["inspections"].append({
                "type": "support_check",
                "inspector": inspector,
                "timestamp": self._timestamp()
            })
            log_event(f"[{self.project_id}] Shoring verified for {zone_id} by {inspector}")

    def mark_pour_complete(self, zone_id: str):
        if zone_id in self.deck_zones:
            self.deck_zones[zone_id]["pour_status"] = "complete"
            log_event(f"[{self.project_id}] Pour completed for deck zone: {zone_id}")

    def get_zone_status(self, zone_id: str):
        return self.deck_zones.get(zone_id, None)

    def _timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()
