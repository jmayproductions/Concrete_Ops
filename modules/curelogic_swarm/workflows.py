"""Named CureLogic curing workflow runners."""
from __future__ import annotations
from typing import Any, Callable
from modules.curelogic_swarm.agents import (
    AmbientWeatherAgent, ColdWeatherCureAgent, CoverBlanketAgent, CrewOpsAgent,
    CureLeadAgent, CurePlanAgent, EvaporationRateAgent, HotWeatherCureAgent,
    MaturityStrengthAgent, MembraneCompoundAgent, MoistureEnvelopeAgent,
    QaInspectorAgent, SafetyFailsafeAgent, SteamAccelAgent, ThermalDeltaAgent, WetCureAgent,
)
from modules.curelogic_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-cure-gate", "evaporation-gate", "thermal-envelope-gate", "wet-cure-gate",
    "membrane-cure-gate", "cover-integrity-gate", "cold-weather-cure-gate",
    "hot-weather-cure-gate", "steam-accel-gate", "day-n-maturity-gate",
    "curing-closeout", "hold-abort",
)

def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"

def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed with curing plan controls", "Log temp/moisture/evap at scheduled checkpoints"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP — protect concrete; do not release forms/load",
            "Preserve cure logs, thermocouple data, photos, timestamps",
            "Re-enter through pre-cure-gate or day-n-maturity-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "cure-lead"]
    return [
        "Do not finish/release until cleared",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]

def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("pour_id") or ctx.get("area") or "ZONE-UNSET"

class WorkflowRunner:
    def __init__(self) -> None:
        self.plan = CurePlanAgent(); self.moisture = MoistureEnvelopeAgent()
        self.evap = EvaporationRateAgent(); self.thermal = ThermalDeltaAgent()
        self.weather = AmbientWeatherAgent(); self.wet = WetCureAgent()
        self.membrane = MembraneCompoundAgent(); self.cover = CoverBlanketAgent()
        self.maturity = MaturityStrengthAgent(); self.cold = ColdWeatherCureAgent()
        self.hot = HotWeatherCureAgent(); self.steam = SteamAccelAgent()
        self.safety = SafetyFailsafeAgent(); self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent(); self.lead = CureLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_cure_gate(self, ctx):
        gates = [self.plan.evaluate(ctx), self.weather.evaluate(ctx), self.evap.evaluate(ctx),
                 self.moisture.evaluate(ctx), self.crew.evaluate(ctx, True), self.safety.evaluate(ctx),
                 self.qa.evaluate(ctx, "pre")]
        return self._finish("pre-cure-gate", ctx, gates, {
            "GO": "Pre-cure clear — finishing/cure may proceed under plan.",
            "HOLD": "Pre-cure holding — plan/weather/evap/moisture.",
            "ABORT": "Pre-cure aborted by fail-safe.",
        })

    def evaporation_gate(self, ctx):
        gates = [self.evap.evaluate(ctx), self.weather.evaluate(ctx), self.hot.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("evaporation-gate", ctx, gates, {
            "GO": "Evaporation risk clear.", "HOLD": "Evaporation holding.",
            "ABORT": "Evaporation aborted — delay pour or aggressive cure.",
        })

    def thermal_envelope_gate(self, ctx):
        gates = [self.thermal.evaluate(ctx), self.cover.evaluate(ctx), self.cold.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("thermal-envelope-gate", ctx, gates, {
            "GO": "Thermal envelope clear.", "HOLD": "Thermal envelope holding.",
            "ABORT": "Thermal envelope aborted — insulate / cool controls.",
        })

    def wet_cure_gate(self, ctx):
        plan = {**(ctx.get("plan") or {}), "method": (ctx.get("plan") or {}).get("method") or "wet_burlap"}
        ctx = {**ctx, "plan": plan}
        gates = [self.wet.evaluate(ctx), self.moisture.evaluate(ctx), self.weather.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("wet-cure-gate", ctx, gates, {
            "GO": "Wet cure clear.", "HOLD": "Wet cure holding.", "ABORT": "Wet cure aborted.",
        })

    def membrane_cure_gate(self, ctx):
        plan = {**(ctx.get("plan") or {}), "method": (ctx.get("plan") or {}).get("method") or "membrane"}
        ctx = {**ctx, "plan": plan}
        gates = [self.membrane.evaluate(ctx), self.moisture.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("membrane-cure-gate", ctx, gates, {
            "GO": "Membrane cure clear.", "HOLD": "Membrane cure holding.", "ABORT": "Membrane cure aborted.",
        })

    def cover_integrity_gate(self, ctx):
        plan = {**(ctx.get("plan") or {}), "method": (ctx.get("plan") or {}).get("method") or "poly_cover"}
        cover = {**(ctx.get("cover") or {}), "required": True}
        ctx = {**ctx, "plan": plan, "cover": cover}
        gates = [self.cover.evaluate(ctx), self.thermal.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("cover-integrity-gate", ctx, gates, {
            "GO": "Cover integrity clear.", "HOLD": "Cover integrity holding.", "ABORT": "Cover integrity aborted.",
        })

    def cold_weather_cure_gate(self, ctx):
        ctx = {**ctx, "cold": {**(ctx.get("cold") or {}), "required": True}}
        gates = [self.cold.evaluate(ctx), self.cover.evaluate(ctx), self.weather.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("cold-weather-cure-gate", ctx, gates, {
            "GO": "Cold-weather curing clear.", "HOLD": "Cold-weather curing holding.",
            "ABORT": "Cold-weather curing aborted — protect from freeze.",
        })

    def hot_weather_cure_gate(self, ctx):
        ctx = {**ctx, "hot": {**(ctx.get("hot") or {}), "required": True}}
        gates = [self.hot.evaluate(ctx), self.evap.evaluate(ctx), self.weather.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("hot-weather-cure-gate", ctx, gates, {
            "GO": "Hot-weather curing clear.", "HOLD": "Hot-weather curing holding.",
            "ABORT": "Hot-weather curing aborted.",
        })

    def steam_accel_gate(self, ctx):
        ctx = {**ctx, "plan": {**(ctx.get("plan") or {}), "method": "steam"},
               "steam": {**(ctx.get("steam") or {}), "required": True}}
        gates = [self.steam.evaluate(ctx), self.thermal.evaluate(ctx), self.maturity.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("steam-accel-gate", ctx, gates, {
            "GO": "Steam/accelerated curing clear.", "HOLD": "Steam/accelerated curing holding.",
            "ABORT": "Steam/accelerated curing aborted.",
        })

    def day_n_maturity_gate(self, ctx):
        ctx = {**ctx, "maturity": {**(ctx.get("maturity") or {}), "release_requested": True, "required": True}}
        gates = [self.maturity.evaluate(ctx), self.plan.evaluate(ctx), self.thermal.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "release")]
        return self._finish("day-n-maturity-gate", ctx, gates, {
            "GO": "Day-N maturity clear for release.", "HOLD": "Day-N maturity holding.",
            "ABORT": "Day-N maturity aborted — do not release.",
        })

    def curing_closeout(self, ctx):
        gates = [self.qa.evaluate(ctx, "release"), self.plan.evaluate(ctx),
                 self.maturity.evaluate(ctx), self.crew.evaluate(ctx, False)]
        return self._finish("curing-closeout", ctx, gates, {
            "GO": "Curing closeout clear.", "HOLD": "Curing closeout holding.", "ABORT": "Curing closeout aborted.",
        })

    def hold_abort(self, ctx):
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult("cure-lead", "FAIL" if decision == "ABORT" else "HOLD", reason,
                            {"owner": ctx.get("owner", "cure_superintendent")})]
        summary = "ABORT escalated — protect concrete and stop release." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))

def get_workflow_handlers(runner: WorkflowRunner | None = None):
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
