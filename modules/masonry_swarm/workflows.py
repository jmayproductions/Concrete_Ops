"""Named masonry workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.masonry_swarm.agents import (
    ControlJointsAgent,
    CrewOpsAgent,
    CureProtectAgent,
    EmbedsAnchorsAgent,
    FlashingWeepsAgent,
    GroutLiftsAgent,
    LayoutCoursingAgent,
    MasonryLeadAgent,
    MaterialsSubmittalAgent,
    MortarQcAgent,
    PlumbToleranceAgent,
    QaInspectorAgent,
    RainscreenVeneerAgent,
    ReinforcementAgent,
    SafetyFailsafeAgent,
    WeatherProtectAgent,
)
from modules.masonry_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-masonry-gate",
    "layout-coursing-gate",
    "daily-layup-runbook",
    "mortar-qc-check",
    "rebar-pregrout-gate",
    "grout-lift-runbook",
    "flashing-weep-qa",
    "plumb-tolerance-check",
    "veneer-rainscreen-gate",
    "weather-protect-gate",
    "masonry-closeout",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next masonry sequence / workflow", "Maintain cure + weep/flashing protection"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — secure unstable walls/scaffold",
            "Preserve photos, mortar/grout logs, timestamps",
            "Re-enter through pre-masonry-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "masonry-lead"]
    return [
        "Do not advance courses / grout / veneer cover",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.materials = MaterialsSubmittalAgent()
        self.layout = LayoutCoursingAgent()
        self.mortar = MortarQcAgent()
        self.rebar = ReinforcementAgent()
        self.grout = GroutLiftsAgent()
        self.flash = FlashingWeepsAgent()
        self.plumb = PlumbToleranceAgent()
        self.weather = WeatherProtectAgent()
        self.cure = CureProtectAgent()
        self.veneer = RainscreenVeneerAgent()
        self.embeds = EmbedsAnchorsAgent()
        self.cj = ControlJointsAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = MasonryLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_masonry_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.materials.evaluate(ctx),
            self.layout.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-masonry-gate", ctx, gates, {
            "GO": "Pre-masonry clear — lay-up may begin.",
            "HOLD": "Pre-masonry holding — materials/layout/weather.",
            "ABORT": "Pre-masonry aborted by fail-safe.",
        })

    def layout_coursing_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.layout.evaluate(ctx), self.plumb.evaluate(ctx), self.qa.evaluate(ctx, phase="pre")]
        return self._finish("layout-coursing-gate", ctx, gates, {
            "GO": "Layout/coursing clear.",
            "HOLD": "Layout holding.",
            "ABORT": "Layout aborted.",
        })

    def daily_layup_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.mortar.evaluate(ctx),
            self.layout.evaluate(ctx),
            self.plumb.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("daily-layup-runbook", ctx, gates, {
            "GO": "Daily lay-up clear.",
            "HOLD": "Daily lay-up holding.",
            "ABORT": "Daily lay-up aborted.",
        })

    def mortar_qc_check(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.mortar.evaluate(ctx), self.qa.evaluate(ctx, phase="during")]
        return self._finish("mortar-qc-check", ctx, gates, {
            "GO": "Mortar QC clear.",
            "HOLD": "Mortar QC holding.",
            "ABORT": "Mortar QC aborted.",
        })

    def rebar_pregrout_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.rebar.evaluate(ctx),
            self.embeds.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("rebar-pregrout-gate", ctx, gates, {
            "GO": "Rebar pre-grout clear.",
            "HOLD": "Rebar/embeds holding — do not grout.",
            "ABORT": "Rebar gate aborted.",
        })

    def grout_lift_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.rebar.evaluate(ctx),
            self.grout.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("grout-lift-runbook", ctx, gates, {
            "GO": "Grout lift clear.",
            "HOLD": "Grout lift holding.",
            "ABORT": "Grout lift aborted.",
        })

    def flashing_weep_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.flash.evaluate(ctx), self.cj.evaluate(ctx), self.qa.evaluate(ctx, phase="during")]
        return self._finish("flashing-weep-qa", ctx, gates, {
            "GO": "Flashing/weeps/control joints clear.",
            "HOLD": "Flashing/weeps holding.",
            "ABORT": "Flashing aborted.",
        })

    def plumb_tolerance_check(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.plumb.evaluate(ctx), self.layout.evaluate(ctx), self.qa.evaluate(ctx, phase="during")]
        return self._finish("plumb-tolerance-check", ctx, gates, {
            "GO": "Plumb/tolerance clear.",
            "HOLD": "Plumb holding.",
            "ABORT": "Plumb aborted.",
        })

    def veneer_rainscreen_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.veneer.evaluate({**ctx, "require_veneer": True}),
            self.flash.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("veneer-rainscreen-gate", ctx, gates, {
            "GO": "Veneer/rainscreen clear.",
            "HOLD": "Veneer holding.",
            "ABORT": "Veneer aborted.",
        })

    def weather_protect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.cure.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-protect-gate", ctx, gates, {
            "GO": "Weather/cure protection clear.",
            "HOLD": "Weather/cure holding.",
            "ABORT": "Weather protect aborted.",
        })

    def masonry_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="post"),
            self.plumb.evaluate(ctx),
            self.flash.evaluate(ctx),
            self.cj.evaluate(ctx),
            self.grout.evaluate(ctx),
            self.cure.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("masonry-closeout", ctx, gates, {
            "GO": "Masonry closeout complete.",
            "HOLD": "Masonry closeout incomplete.",
            "ABORT": "Masonry closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        reason = ctx.get("block_reason") or "unspecified gate failure"
        severity = (ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        gates = [GateResult(
            "safety-failsafe" if decision == "ABORT" else "masonry-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "superintendent")},
        )]
        summary = "ABORT escalated — stop work and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
