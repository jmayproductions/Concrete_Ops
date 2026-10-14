"""Named heavy-lift / crane workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.heavy_lift_swarm.agents import (
    CraneCertsAgent,
    CrewOpsAgent,
    ExclusionZoneAgent,
    GroundBearingAgent,
    LiftLeadAgent,
    LiftPlanAgent,
    LoadChartAgent,
    PickPathAgent,
    PowerLinesAgent,
    QaInspectorAgent,
    RiggingGearAgent,
    SafetyFailsafeAgent,
    SignalCommsAgent,
    TagLineControlAgent,
    TandemCriticalAgent,
    WeatherWindAgent,
)
from modules.heavy_lift_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-lift-gate",
    "lift-plan-review",
    "ground-bearing-gate",
    "rigging-inspection",
    "load-chart-gate",
    "power-line-clearance",
    "exclusion-zone-gate",
    "critical-lift-runbook",
    "tandem-lift-gate",
    "weather-wind-gate",
    "post-lift-closeout",
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
        return ["Proceed with lift under plan controls", "Keep exclusion enforced; re-check wind before pick"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP LIFT — lower/land load if safe; clear exclusion; secure crane",
            "Preserve lift plan, chart sheet, photos, wind log, timestamps",
            "Re-enter through pre-lift-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "lift-lead"]
    return [
        "Do not hoist until cleared",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("pick_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.plan = LiftPlanAgent()
        self.certs = CraneCertsAgent()
        self.ground = GroundBearingAgent()
        self.rigging = RiggingGearAgent()
        self.path = PickPathAgent()
        self.power = PowerLinesAgent()
        self.exclusion = ExclusionZoneAgent()
        self.comms = SignalCommsAgent()
        self.weather = WeatherWindAgent()
        self.chart = LoadChartAgent()
        self.taglines = TagLineControlAgent()
        self.tandem = TandemCriticalAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = LiftLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_lift_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.plan.evaluate(ctx),
            self.certs.evaluate(ctx),
            self.chart.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-lift-gate", ctx, gates, {
            "GO": "Pre-lift clear — setup/pick sequence may proceed.",
            "HOLD": "Pre-lift holding — plan/certs/chart/weather.",
            "ABORT": "Pre-lift aborted by fail-safe.",
        })

    def lift_plan_review(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.plan.evaluate(ctx),
            self.chart.evaluate(ctx),
            self.tandem.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("lift-plan-review", ctx, gates, {
            "GO": "Lift plan review clear.",
            "HOLD": "Lift plan review holding.",
            "ABORT": "Lift plan review aborted.",
        })

    def ground_bearing_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.ground.evaluate(ctx),
            self.certs.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("ground-bearing-gate", ctx, gates, {
            "GO": "Ground bearing/setup clear.",
            "HOLD": "Ground bearing holding.",
            "ABORT": "Ground bearing aborted.",
        })

    def rigging_inspection(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.rigging.evaluate(ctx),
            self.chart.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("rigging-inspection", ctx, gates, {
            "GO": "Rigging inspection clear.",
            "HOLD": "Rigging holding.",
            "ABORT": "Rigging aborted — remove damaged gear.",
        })

    def load_chart_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.chart.evaluate(ctx),
            self.plan.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("load-chart-gate", ctx, gates, {
            "GO": "Load chart clear.",
            "HOLD": "Load chart holding.",
            "ABORT": "Load chart aborted — do not hoist.",
        })

    def power_line_clearance(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.power.evaluate(ctx),
            self.path.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("power-line-clearance", ctx, gates, {
            "GO": "Power line clearance clear.",
            "HOLD": "Power line clearance holding.",
            "ABORT": "Power line aborted — stop boom movement.",
        })

    def exclusion_zone_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.exclusion.evaluate(ctx),
            self.comms.evaluate(ctx),
            self.taglines.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("exclusion-zone-gate", ctx, gates, {
            "GO": "Exclusion/comms clear.",
            "HOLD": "Exclusion/comms holding.",
            "ABORT": "Exclusion aborted — clear people from zone.",
        })

    def critical_lift_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        plan = {**(ctx.get("plan") or {}), "critical": True, "approved": (ctx.get("plan") or {}).get("approved", True)}
        chart = {**(ctx.get("chart") or {}), "critical": True}
        ctx = {**ctx, "plan": plan, "chart": chart}
        gates = [
            self.plan.evaluate(ctx),
            self.chart.evaluate(ctx),
            self.ground.evaluate(ctx),
            self.rigging.evaluate(ctx),
            self.power.evaluate(ctx),
            self.exclusion.evaluate(ctx),
            self.comms.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("critical-lift-runbook", ctx, gates, {
            "GO": "Critical lift runbook clear.",
            "HOLD": "Critical lift holding.",
            "ABORT": "Critical lift aborted.",
        })

    def tandem_lift_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "tandem": {**(ctx.get("tandem") or {}), "required": True}, "plan": {**(ctx.get("plan") or {}), "critical": True}}
        gates = [
            self.tandem.evaluate(ctx),
            self.plan.evaluate(ctx),
            self.comms.evaluate(ctx),
            self.chart.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("tandem-lift-gate", ctx, gates, {
            "GO": "Tandem lift clear.",
            "HOLD": "Tandem lift holding.",
            "ABORT": "Tandem lift aborted.",
        })

    def weather_wind_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-wind-gate", ctx, gates, {
            "GO": "Weather/wind clear for lifting.",
            "HOLD": "Weather holding.",
            "ABORT": "Weather aborted — do not lift.",
        })

    def post_lift_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="closeout"),
            self.rigging.evaluate(ctx),
            self.exclusion.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("post-lift-closeout", ctx, gates, {
            "GO": "Post-lift closeout clear.",
            "HOLD": "Post-lift closeout holding.",
            "ABORT": "Post-lift closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "lift-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "lift_director")},
        )]
        summary = "ABORT escalated — stop lift and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
