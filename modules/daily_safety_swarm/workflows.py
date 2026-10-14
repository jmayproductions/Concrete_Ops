"""Named daily safety workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.daily_safety_swarm.agents import (
    ConfinedSpaceAgent,
    CraneExclusionAgent,
    CrewOpsAgent,
    DailyBriefingAgent,
    ExcavationCompetentAgent,
    FallProtectionAgent,
    FireWatchAgent,
    HotWorkPermitAgent,
    IncidentStopAgent,
    LotoEnergyAgent,
    PpeReadinessAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SafetyLeadAgent,
    SubstanceFatigueAgent,
    WeatherEmergencyAgent,
)
from modules.daily_safety_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-shift-safety-gate",
    "hot-work-permit-gate",
    "confined-space-entry",
    "loto-release-gate",
    "fall-protection-gate",
    "excavation-safety-gate",
    "crane-exclusion-gate",
    "fire-watch-closeout",
    "incident-abort",
    "weather-emergency-gate",
    "end-of-shift-closeout",
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
        return ["Proceed with permitted work under listed controls", "Keep permits posted; re-check if conditions change"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — make area safe; pull permits if violated",
            "Preserve permit sheets, gas logs, photos, timestamps",
            "Re-enter through pre-shift-safety-gate / specific permit gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "safety-lead"]
    return [
        "Do not start/continue high-risk task until cleared",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("task") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.briefing = DailyBriefingAgent()
        self.ppe = PpeReadinessAgent()
        self.hot = HotWorkPermitAgent()
        self.fire = FireWatchAgent()
        self.cse = ConfinedSpaceAgent()
        self.loto = LotoEnergyAgent()
        self.fall = FallProtectionAgent()
        self.excavation = ExcavationCompetentAgent()
        self.crane = CraneExclusionAgent()
        self.incident = IncidentStopAgent()
        self.weather = WeatherEmergencyAgent()
        self.impairment = SubstanceFatigueAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = SafetyLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_shift_safety_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.briefing.evaluate(ctx),
            self.ppe.evaluate(ctx),
            self.impairment.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-shift-safety-gate", ctx, gates, {
            "GO": "Pre-shift safety clear — permitted work may proceed under controls.",
            "HOLD": "Pre-shift safety holding — briefing/PPE/weather.",
            "ABORT": "Pre-shift aborted by fail-safe.",
        })

    def hot_work_permit_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {
            **ctx,
            "hot_work": {**(ctx.get("hot_work") or {}), "required": True, "active": True},
            "fire_watch": {**(ctx.get("fire_watch") or {}), "required": True},
        }
        gates = [
            self.hot.evaluate(ctx),
            self.fire.evaluate(ctx),
            self.ppe.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("hot-work-permit-gate", ctx, gates, {
            "GO": "Hot work permit clear.",
            "HOLD": "Hot work holding.",
            "ABORT": "Hot work aborted — stop welding/cutting.",
        })

    def confined_space_entry(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "cse": {**(ctx.get("cse") or {}), "required": True}}
        gates = [
            self.cse.evaluate(ctx),
            self.ppe.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("confined-space-entry", ctx, gates, {
            "GO": "Confined space entry clear.",
            "HOLD": "Confined space holding.",
            "ABORT": "Confined space aborted — evacuate/stop entry.",
        })

    def loto_release_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "loto": {**(ctx.get("loto") or {}), "required": True}}
        gates = [
            self.loto.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("loto-release-gate", ctx, gates, {
            "GO": "LOTO clear for work.",
            "HOLD": "LOTO holding.",
            "ABORT": "LOTO aborted — do not touch equipment.",
        })

    def fall_protection_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "fall": {**(ctx.get("fall") or {}), "required": True}}
        gates = [
            self.fall.evaluate(ctx),
            self.ppe.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("fall-protection-gate", ctx, gates, {
            "GO": "Fall protection clear.",
            "HOLD": "Fall protection holding.",
            "ABORT": "Fall protection aborted.",
        })

    def excavation_safety_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "excavation": {**(ctx.get("excavation") or {}), "required": True}}
        gates = [
            self.excavation.evaluate(ctx),
            self.ppe.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("excavation-safety-gate", ctx, gates, {
            "GO": "Excavation safety clear.",
            "HOLD": "Excavation safety holding.",
            "ABORT": "Excavation safety aborted.",
        })

    def crane_exclusion_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "crane": {**(ctx.get("crane") or {}), "required": True}}
        gates = [
            self.crane.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("crane-exclusion-gate", ctx, gates, {
            "GO": "Crane exclusion clear.",
            "HOLD": "Crane exclusion holding.",
            "ABORT": "Crane exclusion aborted.",
        })

    def fire_watch_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {
            **ctx,
            "hot_work": {**(ctx.get("hot_work") or {}), "required": True},
            "fire_watch": {**(ctx.get("fire_watch") or {}), "required": True},
        }
        gates = [
            self.fire.evaluate(ctx),
            self.hot.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("fire-watch-closeout", ctx, gates, {
            "GO": "Fire watch closeout clear.",
            "HOLD": "Fire watch closeout holding.",
            "ABORT": "Fire watch closeout aborted.",
        })

    def incident_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "incident": {**(ctx.get("incident") or {}), "stop_work": True}}
        gates = [self.incident.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("incident-abort", ctx, gates, {
            "GO": "No incident path (unexpected).",
            "HOLD": "Incident holding.",
            "ABORT": "Incident/stop-work — secure scene.",
        })

    def weather_emergency_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-emergency-gate", ctx, gates, {
            "GO": "Weather/emergency clear.",
            "HOLD": "Weather holding.",
            "ABORT": "Emergency — evacuate/stop.",
        })

    def end_of_shift_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="closeout"),
            self.hot.evaluate(ctx),
            self.cse.evaluate(ctx),
            self.loto.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("end-of-shift-closeout", ctx, gates, {
            "GO": "End-of-shift safety closeout clear.",
            "HOLD": "End-of-shift closeout holding.",
            "ABORT": "End-of-shift closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "safety-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "site_safety")},
        )]
        summary = "ABORT escalated — stop work and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
