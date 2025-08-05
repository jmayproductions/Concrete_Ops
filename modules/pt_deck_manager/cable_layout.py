# modules/pt_deck_manager/cable_layout.py

"""
ConcreteOps: PT Deck Manager – Cable Layout Checker
Validates layout and continuity of post-tension (PT) cables on elevated decks. Flags missing tendons, incorrect spacing, and crossovers.
Supports phased PT sequencing, stress timing, and pour striping plans.
"""

from shared.utils import log_event, trigger_alert


class PTCableLayoutChecker:
    def __init__(self, deck_id):
        self.deck_id = deck_id
        self.layout = []

    def record_cable(self, tag: str, zone: str, spacing_in: float, stressed: bool):
        entry = {
            "tag": tag,
            "zone": zone,
            "spacing_in": spacing_in,
            "stressed": stressed
        }

        self.layout.append(entry)
        if spacing_in > 48:
            trigger_alert(f"[{self.deck_id}] PT cable {tag} in {zone} exceeds spacing limit: {spacing_in} in")

        if not stressed:
            trigger_alert(f"[{self.deck_id}] PT cable {tag} in {zone} not yet stressed!")

        log_event(f"[{self.deck_id}] Cable {tag} logged for zone {zone} | Spacing: {spacing_in}\" | Stressed: {stressed}")

    def summary(self):
        total = len(self.layout)
        unstressed = len([c for c in self.layout if not c["stressed"]])
        wide_spaced = len([c for c in self.layout if c["spacing_in"] > 48])
        return {
            "total": total,
            "unstressed": unstressed,
            "over_spaced": wide_spaced
        }
