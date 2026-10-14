"""Named SOE / shoring workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.soe_swarm.agents import (
    BraceReleaseAgent,
    CrewOpsAgent,
    DesignSubmittalAgent,
    DewateringAgent,
    ExcavationStagesAgent,
    LaggingAgent,
    LoadMonitoringAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SheetPileAgent,
    SoeLeadAgent,
    SoldierPilesAgent,
    SurveyMonitoringAgent,
    TiebacksAnchorsAgent,
    WalesStrutsAgent,
    WeatherProtectAgent,
)
from modules.soe_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-soe-gate",
    "pile-install-runbook",
    "lagging-install-gate",
    "excavation-stage-gate",
    "strut-waler-gate",
    "tieback-test-gate",
    "monitoring-alarm-gate",
    "dewatering-gate",
    "brace-release-gate",
    "weather-protect-gate",
    "soe-closeout",
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
        return ["Proceed to next SOE sequence / workflow", "Keep monitoring + stage logs current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — backfill/secure face; clear exclusion zone; call engineer",
            "Preserve monitoring plots, stage depths, photos, timestamps",
            "Re-enter through pre-soe-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "soe-lead"]
    return [
        "Do not deepen excavate / release braces",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.design = DesignSubmittalAgent()
        self.monitoring = SurveyMonitoringAgent()
        self.soldier = SoldierPilesAgent()
        self.lagging = LaggingAgent()
        self.sheet = SheetPileAgent()
        self.bracing = WalesStrutsAgent()
        self.tiebacks = TiebacksAnchorsAgent()
        self.excavation = ExcavationStagesAgent()
        self.dewatering = DewateringAgent()
        self.loads = LoadMonitoringAgent()
        self.release = BraceReleaseAgent()
        self.weather = WeatherProtectAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = SoeLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_soe_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.design.evaluate(ctx),
            self.monitoring.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-soe-gate", ctx, gates, {
            "GO": "Pre-SOE clear — install/excavate sequence may proceed.",
            "HOLD": "Pre-SOE holding — design/monitoring/weather.",
            "ABORT": "Pre-SOE aborted by fail-safe.",
        })

    def pile_install_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.design.evaluate(ctx),
            self.soldier.evaluate(ctx),
            self.sheet.evaluate(ctx),
            self.monitoring.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("pile-install-runbook", ctx, gates, {
            "GO": "Pile/sheet install clear.",
            "HOLD": "Pile/sheet install holding.",
            "ABORT": "Pile/sheet install aborted.",
        })

    def lagging_install_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "lagging": {**(ctx.get("lagging") or {}), "required": True}}
        gates = [
            self.lagging.evaluate(ctx),
            self.excavation.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("lagging-install-gate", ctx, gates, {
            "GO": "Lagging install clear.",
            "HOLD": "Lagging holding.",
            "ABORT": "Lagging aborted.",
        })

    def excavation_stage_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.excavation.evaluate(ctx),
            self.bracing.evaluate(ctx),
            self.tiebacks.evaluate(ctx),
            self.monitoring.evaluate(ctx),
            self.dewatering.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("excavation-stage-gate", ctx, gates, {
            "GO": "Excavation stage clear.",
            "HOLD": "Excavation stage holding.",
            "ABORT": "Excavation stage aborted — secure face.",
        })

    def strut_waler_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "bracing": {**(ctx.get("bracing") or {}), "required": True}}
        gates = [
            self.bracing.evaluate(ctx),
            self.loads.evaluate(ctx),
            self.monitoring.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("strut-waler-gate", ctx, gates, {
            "GO": "Strut/waler clear.",
            "HOLD": "Strut/waler holding.",
            "ABORT": "Strut/waler aborted.",
        })

    def tieback_test_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "tiebacks": {**(ctx.get("tiebacks") or {}), "required": True}}
        gates = [
            self.tiebacks.evaluate(ctx),
            self.loads.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("tieback-test-gate", ctx, gates, {
            "GO": "Tieback testing clear.",
            "HOLD": "Tieback testing holding.",
            "ABORT": "Tieback testing aborted.",
        })

    def monitoring_alarm_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.monitoring.evaluate(ctx),
            self.loads.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("monitoring-alarm-gate", ctx, gates, {
            "GO": "Monitoring within limits.",
            "HOLD": "Monitoring alert — eng review.",
            "ABORT": "Monitoring alarm — stop work.",
        })

    def dewatering_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.dewatering.evaluate(ctx),
            self.excavation.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("dewatering-gate", ctx, gates, {
            "GO": "Dewatering clear.",
            "HOLD": "Dewatering holding.",
            "ABORT": "Dewatering aborted.",
        })

    def brace_release_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "release": {**(ctx.get("release") or {}), "required": True}}
        gates = [
            self.release.evaluate(ctx),
            self.monitoring.evaluate(ctx),
            self.loads.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("brace-release-gate", ctx, gates, {
            "GO": "Brace release sequence clear.",
            "HOLD": "Brace release holding.",
            "ABORT": "Brace release aborted.",
        })

    def weather_protect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.weather.evaluate(ctx),
            self.dewatering.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish("weather-protect-gate", ctx, gates, {
            "GO": "Weather/protection clear.",
            "HOLD": "Weather holding.",
            "ABORT": "Weather aborted.",
        })

    def soe_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "release": {**(ctx.get("release") or {}), "required": True}}
        gates = [
            self.qa.evaluate(ctx, phase="closeout"),
            self.monitoring.evaluate(ctx),
            self.release.evaluate(ctx),
            self.loads.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("soe-closeout", ctx, gates, {
            "GO": "SOE closeout clear.",
            "HOLD": "SOE closeout holding.",
            "ABORT": "SOE closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "soe-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "superintendent")},
        )]
        summary = "ABORT escalated — stop work and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
