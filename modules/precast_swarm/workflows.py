"""Named precast / panelized workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.precast_swarm.agents import (
    BraceReleaseAgent,
    ConnectionsAgent,
    CraneRiggingAgent,
    CrewOpsAgent,
    FabReleaseAgent,
    FinishProtectAgent,
    GroutJointsAgent,
    HybridInterfaceAgent,
    PanelSetAgent,
    PanelSupplyAgent,
    PrecastLeadAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SurveyEmbedsAgent,
    TempBracingAgent,
    WeatherGateAgent,
)
from modules.precast_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-erect-gate",
    "fab-release-gate",
    "delivery-panel-gate",
    "lift-day-runbook",
    "panel-set-qa",
    "bracing-lock",
    "connection-grout-qa",
    "brace-release-gate",
    "hybrid-interface-gate",
    "level-closeout",
    "weather-lift-hold",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status == "FAIL" and g.agent != "precast-lead" for g in active):
        return "HOLD"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next panel pick / workflow", "Maintain braces + lift logs"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP LIFTS — secure unbraced panels",
            "Preserve panel tags, photos, strength/brace logs, timestamps",
            "Re-enter through pre-erect-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "precast-lead"]
    return [
        "Do not advance panel sequence",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("erect_id") or ctx.get("area") or "ERECT-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.fab = FabReleaseAgent()
        self.supply = PanelSupplyAgent()
        self.survey = SurveyEmbedsAgent()
        self.crane = CraneRiggingAgent()
        self.bracing = TempBracingAgent()
        self.panels = PanelSetAgent()
        self.connections = ConnectionsAgent()
        self.grout = GroutJointsAgent()
        self.hybrid = HybridInterfaceAgent()
        self.finish = FinishProtectAgent()
        self.brace_release = BraceReleaseAgent()
        self.weather = WeatherGateAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = PrecastLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_erect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.fab.evaluate(ctx),
            self.supply.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.crane.evaluate(ctx),
            self.bracing.plan(ctx),
            self.hybrid.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-erect-gate", ctx, gates, {
            "GO": "Pre-erect clear — panel lifts may begin.",
            "HOLD": "Pre-erect holding — fab/survey/crane/bracing.",
            "ABORT": "Pre-erect aborted by fail-safe.",
        })

    def fab_release_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.fab.evaluate(ctx), self.qa.evaluate(ctx, phase="pre"), self.safety.evaluate(ctx)]
        return self._finish("fab-release-gate", ctx, gates, {
            "GO": "Fab/strength release clear.",
            "HOLD": "Fab release holding.",
            "ABORT": "Fab release aborted.",
        })

    def delivery_panel_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.supply.evaluate(ctx),
            self.crane.evaluate(ctx),
            self.finish.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish("delivery-panel-gate", ctx, gates, {
            "GO": "Delivery/panel tags clear.",
            "HOLD": "Delivery holding.",
            "ABORT": "Delivery aborted.",
        })

    def lift_day_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.crane.evaluate(ctx),
            self.fab.evaluate(ctx),
            self.panels.evaluate(ctx),
            self.bracing.lock_in(ctx) if (ctx.get("bracing") or {}).get("braces_installed") is not None else self.bracing.plan(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("lift-day-runbook", ctx, gates, {
            "GO": "Lift day clear.",
            "HOLD": "Lift day holding.",
            "ABORT": "Lift day aborted — stop picks.",
        })

    def panel_set_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.panels.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.connections.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("panel-set-qa", ctx, gates, {
            "GO": "Panel set QA clear.",
            "HOLD": "Panel set holding.",
            "ABORT": "Panel set aborted.",
        })

    def bracing_lock(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.bracing.lock_in(ctx),
            self.panels.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("bracing-lock", ctx, gates, {
            "GO": "Bracing locked.",
            "HOLD": "Bracing not locked.",
            "ABORT": "Bracing abort — unstable panel.",
        })

    def connection_grout_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.connections.evaluate(ctx),
            self.grout.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("connection-grout-qa", ctx, gates, {
            "GO": "Connections/grout clear.",
            "HOLD": "Connections/grout holding.",
            "ABORT": "Connections aborted.",
        })

    def brace_release_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.brace_release.evaluate(ctx),
            self.connections.evaluate(ctx),
            self.bracing.lock_in(ctx) if (ctx.get("bracing") or {}).get("braces_installed") is not None else self.bracing.plan(ctx),
            self.qa.evaluate(ctx, phase="post"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("brace-release-gate", ctx, gates, {
            "GO": "Brace release clear.",
            "HOLD": "Brace release holding.",
            "ABORT": "Brace release aborted.",
        })

    def hybrid_interface_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.hybrid.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.supply.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("hybrid-interface-gate", ctx, gates, {
            "GO": "Hybrid interface released.",
            "HOLD": "Hybrid interface holding.",
            "ABORT": "Hybrid interface aborted.",
        })

    def level_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="post"),
            self.connections.evaluate(ctx),
            self.grout.evaluate(ctx),
            self.brace_release.evaluate(ctx),
            self.finish.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("level-closeout", ctx, gates, {
            "GO": "Level closeout complete.",
            "HOLD": "Level closeout incomplete.",
            "ABORT": "Level closeout aborted.",
        })

    def weather_lift_hold(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.crane.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-lift-hold", ctx, gates, {
            "GO": "Weather clear for lifts.",
            "HOLD": "Weather holding lifts.",
            "ABORT": "Weather abort.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        reason = ctx.get("block_reason") or "unspecified gate failure"
        severity = (ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        gates = [GateResult(
            "safety-failsafe" if decision == "ABORT" else "precast-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "superintendent")},
        )]
        summary = "ABORT escalated — stop lifts and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
