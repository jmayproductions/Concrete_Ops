"""Named deep foundation workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.deep_foundations_swarm.agents import (
    CageRebarAgent,
    CapacityAcceptanceAgent,
    CasingSlurryAgent,
    ConcretePlacementAgent,
    CrewOpsAgent,
    DrillingAugerAgent,
    FoundationsLeadAgent,
    GeotechAgent,
    IntegrityTestingAgent,
    MaterialsConcreteAgent,
    PileDrivingAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SurveyLayoutAgent,
    TipElevationAgent,
    WeatherProtectAgent,
)
from modules.deep_foundations_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-foundation-gate",
    "layout-stake-gate",
    "drilled-shaft-runbook",
    "tip-elevation-gate",
    "cage-placement-gate",
    "tremie-pour-runbook",
    "driven-pile-runbook",
    "integrity-test-gate",
    "capacity-accept-gate",
    "weather-protect-gate",
    "foundations-closeout",
    "hold-abort",
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
        return ["Proceed to next foundation sequence / workflow", "Keep shaft/pile logs + integrity records current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — cover/secure open holes; clear exclusion zone",
            "Preserve tip photos, volumes, PDA/CSL data, timestamps",
            "Re-enter through pre-foundation-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "foundations-lead"]
    return [
        "Do not advance cage / concrete / drive / cap pour",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("element_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.materials = MaterialsConcreteAgent()
        self.survey = SurveyLayoutAgent()
        self.drilling = DrillingAugerAgent()
        self.casing = CasingSlurryAgent()
        self.tip = TipElevationAgent()
        self.cage = CageRebarAgent()
        self.concrete = ConcretePlacementAgent()
        self.driving = PileDrivingAgent()
        self.integrity = IntegrityTestingAgent()
        self.capacity = CapacityAcceptanceAgent()
        self.weather = WeatherProtectAgent()
        self.geotech = GeotechAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = FoundationsLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_foundation_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.materials.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
            self.geotech.evaluate(ctx),
        ]
        return self._finish("pre-foundation-gate", ctx, gates, {
            "GO": "Pre-foundation clear — drill/drive sequence may proceed.",
            "HOLD": "Pre-foundation holding — materials/layout/weather.",
            "ABORT": "Pre-foundation aborted by fail-safe.",
        })

    def layout_stake_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.survey.evaluate(ctx), self.qa.evaluate(ctx, phase="pre"), self.safety.evaluate(ctx)]
        return self._finish("layout-stake-gate", ctx, gates, {
            "GO": "Layout/stake clear.",
            "HOLD": "Layout holding.",
            "ABORT": "Layout aborted.",
        })

    def drilled_shaft_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "drilling": {**(ctx.get("drilling") or {}), "required": True}}
        gates = [
            self.survey.evaluate(ctx),
            self.drilling.evaluate(ctx),
            self.casing.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("drilled-shaft-runbook", ctx, gates, {
            "GO": "Drilled shaft excavation clear.",
            "HOLD": "Drilled shaft holding.",
            "ABORT": "Drilled shaft aborted — secure hole.",
        })

    def tip_elevation_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "require_tip_si": True}
        gates = [
            self.tip.evaluate(ctx),
            self.geotech.evaluate(ctx),
            self.casing.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("tip-elevation-gate", ctx, gates, {
            "GO": "Tip elevation/cleanout accepted.",
            "HOLD": "Tip holding — cleanout/stratum.",
            "ABORT": "Tip aborted.",
        })

    def cage_placement_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.cage.evaluate(ctx),
            self.tip.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("cage-placement-gate", ctx, gates, {
            "GO": "Cage placement clear.",
            "HOLD": "Cage holding.",
            "ABORT": "Cage aborted.",
        })

    def tremie_pour_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        conc = {**(ctx.get("concrete") or {}), "required": True, "wet_hole": True, "tremie": (ctx.get("concrete") or {}).get("tremie", True)}
        ctx = {**ctx, "concrete": conc}
        gates = [
            self.materials.evaluate(ctx),
            self.cage.evaluate(ctx),
            self.concrete.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("tremie-pour-runbook", ctx, gates, {
            "GO": "Tremie pour clear.",
            "HOLD": "Tremie pour holding.",
            "ABORT": "Tremie pour aborted.",
        })

    def driven_pile_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "driving": {**(ctx.get("driving") or {}), "required": True}}
        gates = [
            self.materials.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.driving.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.geotech.evaluate(ctx),
        ]
        return self._finish("driven-pile-runbook", ctx, gates, {
            "GO": "Driven pile criteria clear.",
            "HOLD": "Driven pile holding.",
            "ABORT": "Driven pile aborted.",
        })

    def integrity_test_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.integrity.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.geotech.evaluate(ctx),
        ]
        return self._finish("integrity-test-gate", ctx, gates, {
            "GO": "Integrity testing clear.",
            "HOLD": "Integrity testing holding.",
            "ABORT": "Integrity testing aborted.",
        })

    def capacity_accept_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.capacity.evaluate(ctx),
            self.integrity.evaluate(ctx),
            self.geotech.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("capacity-accept-gate", ctx, gates, {
            "GO": "Capacity acceptance clear.",
            "HOLD": "Capacity holding.",
            "ABORT": "Capacity aborted.",
        })

    def weather_protect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-protect-gate", ctx, gates, {
            "GO": "Weather/protection clear.",
            "HOLD": "Weather holding.",
            "ABORT": "Weather aborted.",
        })

    def foundations_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="closeout"),
            self.survey.evaluate(ctx),
            self.integrity.evaluate(ctx),
            self.capacity.evaluate(ctx),
            self.geotech.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("foundations-closeout", ctx, gates, {
            "GO": "Foundations closeout clear.",
            "HOLD": "Foundations closeout holding.",
            "ABORT": "Foundations closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "foundations-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "superintendent")},
        )]
        summary = "ABORT escalated — stop work and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
