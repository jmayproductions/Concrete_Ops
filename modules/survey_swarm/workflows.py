"""Named survey / layout workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.survey_swarm.agents import (
    AsBuiltAgent,
    BenchmarksAgent,
    BimLayoutAgent,
    ControlNetworkAgent,
    CrewOpsAgent,
    EmbedsAnchorLayoutAgent,
    EquipmentCalibrationAgent,
    GradeCheckingAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    StakeoutAgent,
    SurveyLeadAgent,
    ToleranceCheckAgent,
    UtilityLocateCoordAgent,
    WeatherProtectAgent,
)
from modules.survey_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-survey-gate",
    "control-network-gate",
    "stakeout-runbook",
    "embed-layout-gate",
    "grade-check-gate",
    "as-built-capture",
    "tolerance-accept-gate",
    "bim-layout-gate",
    "calibration-gate",
    "weather-protect-gate",
    "survey-closeout",
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
        return ["Proceed to next survey/layout sequence", "Protect control + file cut sheets/as-builts"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — re-establish control; clear edge/traffic/utility hazards",
            "Preserve field books, coordinates, photos, timestamps",
            "Re-enter through pre-survey-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "survey-lead"]
    return [
        "Do not pour / pave / cover to unverified layout",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.control = ControlNetworkAgent()
        self.benchmarks = BenchmarksAgent()
        self.stakeout = StakeoutAgent()
        self.asbuilt = AsBuiltAgent()
        self.tolerance = ToleranceCheckAgent()
        self.bim = BimLayoutAgent()
        self.embeds = EmbedsAnchorLayoutAgent()
        self.grade = GradeCheckingAgent()
        self.equipment = EquipmentCalibrationAgent()
        self.utilities = UtilityLocateCoordAgent()
        self.weather = WeatherProtectAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = SurveyLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_survey_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.equipment.evaluate(ctx),
            self.control.evaluate(ctx),
            self.benchmarks.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-survey-gate", ctx, gates, {
            "GO": "Pre-survey clear — layout may proceed.",
            "HOLD": "Pre-survey holding — control/calibration/weather.",
            "ABORT": "Pre-survey aborted by fail-safe.",
        })

    def control_network_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.control.evaluate(ctx),
            self.benchmarks.evaluate(ctx),
            self.equipment.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("control-network-gate", ctx, gates, {
            "GO": "Control network clear.",
            "HOLD": "Control network holding.",
            "ABORT": "Control network aborted.",
        })

    def stakeout_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.control.evaluate(ctx),
            self.stakeout.evaluate(ctx),
            self.bim.evaluate(ctx),
            self.utilities.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("stakeout-runbook", ctx, gates, {
            "GO": "Stake-out clear.",
            "HOLD": "Stake-out holding.",
            "ABORT": "Stake-out aborted.",
        })

    def embed_layout_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "embeds": {**(ctx.get("embeds") or {}), "required": True}}
        gates = [
            self.embeds.evaluate(ctx),
            self.stakeout.evaluate(ctx),
            self.tolerance.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("embed-layout-gate", ctx, gates, {
            "GO": "Embed/anchor layout clear.",
            "HOLD": "Embed layout holding.",
            "ABORT": "Embed layout aborted.",
        })

    def grade_check_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.grade.evaluate(ctx),
            self.benchmarks.evaluate(ctx),
            self.tolerance.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("grade-check-gate", ctx, gates, {
            "GO": "Grade check clear.",
            "HOLD": "Grade check holding.",
            "ABORT": "Grade check aborted.",
        })

    def as_built_capture(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "asbuilt": {**(ctx.get("asbuilt") or {}), "required": True}}
        gates = [
            self.asbuilt.evaluate(ctx),
            self.tolerance.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("as-built-capture", ctx, gates, {
            "GO": "As-built capture clear.",
            "HOLD": "As-built capture holding.",
            "ABORT": "As-built capture aborted.",
        })

    def tolerance_accept_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.tolerance.evaluate(ctx),
            self.asbuilt.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("tolerance-accept-gate", ctx, gates, {
            "GO": "Tolerance acceptance clear.",
            "HOLD": "Tolerance acceptance holding.",
            "ABORT": "Tolerance acceptance aborted.",
        })

    def bim_layout_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "bim": {**(ctx.get("bim") or {}), "required": True}}
        gates = [
            self.bim.evaluate(ctx),
            self.stakeout.evaluate(ctx),
            self.equipment.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("bim-layout-gate", ctx, gates, {
            "GO": "BIM layout clear.",
            "HOLD": "BIM layout holding.",
            "ABORT": "BIM layout aborted.",
        })

    def calibration_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.equipment.evaluate(ctx),
            self.control.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("calibration-gate", ctx, gates, {
            "GO": "Calibration clear.",
            "HOLD": "Calibration holding.",
            "ABORT": "Calibration aborted.",
        })

    def weather_protect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-protect-gate", ctx, gates, {
            "GO": "Weather/visibility clear.",
            "HOLD": "Weather holding.",
            "ABORT": "Weather aborted.",
        })

    def survey_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "asbuilt": {**(ctx.get("asbuilt") or {}), "required": True}}
        gates = [
            self.qa.evaluate(ctx, phase="closeout"),
            self.asbuilt.evaluate(ctx),
            self.control.evaluate(ctx),
            self.tolerance.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("survey-closeout", ctx, gates, {
            "GO": "Survey closeout clear.",
            "HOLD": "Survey closeout holding.",
            "ABORT": "Survey closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "survey-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "chief_of_parties")},
        )]
        summary = "ABORT escalated — stop work and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
