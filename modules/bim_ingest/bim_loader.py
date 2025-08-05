# modules/bim_ingest/bim_loader.py

"""
ConcreteOps: BIM Loader
Ingests IFC model data for clash detection, embed validation, and site layout integration.
Supports lightweight parsing of IFC structural elements and exports key metadata for logic modules.
"""

import ifcopenshell
from shared.utils import log_event


class BIMLoader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.model = None

    def load(self):
        try:
            self.model = ifcopenshell.open(self.filepath)
            log_event(f"BIM file loaded: {self.filepath}")
            return True
        except Exception as e:
            log_event(f"BIM load error: {e}")
            return False

    def get_structural_elements(self):
        """
        Extracts slabs, columns, beams, and footings from the IFC model.
        Returns a list of element dicts with type, GUID, and basic geometry refs.
        """
        elements = []
        types = ["IfcSlab", "IfcColumn", "IfcBeam", "IfcFooting"]
        for t in types:
            for obj in self.model.by_type(t):
                elements.append({
                    "type": t,
                    "guid": obj.GlobalId,
                    "name": obj.Name,
                    "tag": getattr(obj, "Tag", None),
                })
        log_event(f"Extracted {len(elements)} structural elements from BIM.")
        return elements

    def get_embeds_and_inserts(self):
        """
        Extracts embedded parts or sleeves (custom: IfcBuildingElementProxy or IfcMechanicalFastener)
        """
        embeds = []
        for obj in self.model.by_type("IfcBuildingElementProxy"):
            embeds.append({
                "guid": obj.GlobalId,
                "name": obj.Name,
                "object_type": obj.ObjectType
            })
        return embeds
