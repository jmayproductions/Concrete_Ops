"""Named Roofing QAQC workflow runners."""
from __future__ import annotations
from typing import Any, Callable
from modules.roofing_swarm.agents import (
    CrewOpsAgent, DeckPrepAgent, FastenerPatternAgent, FlashingDetailsAgent,
    HighWindZoneAgent, IceWaterShieldAgent, MembraneFlatAgent, PenetrationsBootsAgent,
    QaInspectorAgent, RidgeVentAgent, RoofLeadAgent, SafetyFailsafeAgent, SafetyFallAgent,
    ShinglePlacementAgent, UnderlaymentAgent, ValleyFlashingAgent,
)
from modules.roofing_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-roof-gate", "deck-prep-gate", "underlayment-gate", "fastener-gate",
    "shingle-course-gate", "flashing-gate", "valley-penetration-gate",
    "membrane-flat-gate", "high-wind-gate", "ridge-closeout",
    "final-inspection", "hold-abort",
)

def _decide(gates):
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.status == "FAIL" for g in active): return "ABORT"
    if any(g.status in ("FAIL", "HOLD") for g in active): return "HOLD"
    return "GO"

def _actions(decision, gates):
    if decision == "GO":
        return ["Proceed under roofing ITP controls", "Photo-log fasteners, flashing, and underlayment"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP roofing — weather in / protect openings; fix critical defects",
            "Preserve photos, nail maps, flashing details, timestamps",
            "Re-enter through pre-roof-gate or flashing-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "roof-lead"]
    return ["Do not cover up until cleared",
            *[f"Clear {g.agent}: {g.detail}" for g in holds],
            "Re-run failed gates + safety-failsafe before release"]

def _id(ctx):
    return ctx.get("zone_id") or ctx.get("roof_id") or ctx.get("area") or "ZONE-UNSET"

class WorkflowRunner:
    def __init__(self):
        self.deck = DeckPrepAgent(); self.under = UnderlaymentAgent()
        self.ice = IceWaterShieldAgent(); self.fast = FastenerPatternAgent()
        self.shingles = ShinglePlacementAgent(); self.flash = FlashingDetailsAgent()
        self.valley = ValleyFlashingAgent(); self.pens = PenetrationsBootsAgent()
        self.ridge = RidgeVentAgent(); self.membrane = MembraneFlatAgent()
        self.wind = HighWindZoneAgent(); self.fall = SafetyFallAgent()
        self.safety = SafetyFailsafeAgent(); self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent(); self.lead = RoofLeadAgent()

    def _finish(self, workflow, ctx, gates, summaries):
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_roof_gate(self, ctx):
        gates = [self.deck.evaluate(ctx), self.under.evaluate(ctx), self.ice.evaluate(ctx),
                 self.crew.evaluate(ctx, True), self.fall.evaluate(ctx), self.safety.evaluate(ctx),
                 self.qa.evaluate(ctx, "pre")]
        return self._finish("pre-roof-gate", ctx, gates, {
            "GO": "Pre-roof clear — underlayment/field may proceed.",
            "HOLD": "Pre-roof holding — deck/underlay/ice/fall.",
            "ABORT": "Pre-roof aborted by fail-safe.",
        })

    def deck_prep_gate(self, ctx):
        gates = [self.deck.evaluate(ctx), self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("deck-prep-gate", ctx, gates, {
            "GO": "Deck prep clear.", "HOLD": "Deck prep holding.", "ABORT": "Deck prep aborted.",
        })

    def underlayment_gate(self, ctx):
        gates = [self.under.evaluate(ctx), self.ice.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("underlayment-gate", ctx, gates, {
            "GO": "Underlayment clear.", "HOLD": "Underlayment holding.", "ABORT": "Underlayment aborted.",
        })

    def fastener_gate(self, ctx):
        gates = [self.fast.evaluate(ctx), self.wind.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("fastener-gate", ctx, gates, {
            "GO": "Fastener pattern clear.", "HOLD": "Fastener holding.",
            "ABORT": "Fastener aborted — fix nail pattern before cover-up.",
        })

    def shingle_course_gate(self, ctx):
        gates = [self.shingles.evaluate(ctx), self.fast.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("shingle-course-gate", ctx, gates, {
            "GO": "Shingle courses clear.", "HOLD": "Shingle courses holding.", "ABORT": "Shingle courses aborted.",
        })

    def flashing_gate(self, ctx):
        gates = [self.flash.evaluate(ctx), self.valley.evaluate(ctx), self.pens.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("flashing-gate", ctx, gates, {
            "GO": "Flashing clear.", "HOLD": "Flashing holding.", "ABORT": "Flashing aborted — leak-critical.",
        })

    def valley_penetration_gate(self, ctx):
        gates = [self.valley.evaluate(ctx), self.pens.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("valley-penetration-gate", ctx, gates, {
            "GO": "Valley/penetrations clear.", "HOLD": "Valley/penetrations holding.",
            "ABORT": "Valley/penetrations aborted.",
        })

    def membrane_flat_gate(self, ctx):
        ctx = {**ctx, "membrane": {**(ctx.get("membrane") or {}), "required": True},
               "shingles": {**(ctx.get("shingles") or {}), "system": "membrane", "required": False}}
        gates = [self.membrane.evaluate(ctx), self.pens.evaluate(ctx), self.deck.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("membrane-flat-gate", ctx, gates, {
            "GO": "Membrane/flat clear.", "HOLD": "Membrane/flat holding.", "ABORT": "Membrane/flat aborted.",
        })

    def high_wind_gate(self, ctx):
        ctx = {**ctx, "zone": {**(ctx.get("zone") or {}), "high_wind": True}}
        gates = [self.wind.evaluate(ctx), self.fast.evaluate(ctx), self.shingles.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("high-wind-gate", ctx, gates, {
            "GO": "High-wind roofing clear.", "HOLD": "High-wind holding.", "ABORT": "High-wind aborted.",
        })

    def ridge_closeout(self, ctx):
        gates = [self.ridge.evaluate(ctx), self.shingles.evaluate(ctx), self.qa.evaluate(ctx, "final")]
        return self._finish("ridge-closeout", ctx, gates, {
            "GO": "Ridge closeout clear.", "HOLD": "Ridge closeout holding.", "ABORT": "Ridge closeout aborted.",
        })

    def final_inspection(self, ctx):
        gates = [self.qa.evaluate(ctx, "final"), self.flash.evaluate(ctx), self.fast.evaluate(ctx),
                 self.ridge.evaluate(ctx), self.safety.evaluate(ctx), self.crew.evaluate(ctx, False)]
        return self._finish("final-inspection", ctx, gates, {
            "GO": "Final roof inspection clear.", "HOLD": "Final inspection holding.",
            "ABORT": "Final inspection aborted.",
        })

    def hold_abort(self, ctx):
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult("roof-lead", "FAIL" if decision == "ABORT" else "HOLD", reason,
                            {"owner": ctx.get("owner", "roof_superintendent")})]
        summary = "ABORT escalated — stop cover-up and weather in." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))

def get_workflow_handlers(runner=None):
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
