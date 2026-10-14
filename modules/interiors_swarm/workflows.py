"""Named interiors / drywall workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.interiors_swarm.agents import (
    AcousticsStcAgent,
    BlockingBackingAgent,
    BoardHangAgent,
    CrewOpsAgent,
    FireRatedAssembliesAgent,
    InteriorsLeadAgent,
    InwallCoverReleaseAgent,
    LayoutControlAgent,
    MaterialsSubmittalAgent,
    MetalStudFramingAgent,
    OpeningsDoorsAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    ShaftwallAgent,
    TapingFinishAgent,
    WeatherProtectAgent,
)
from modules.interiors_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-interiors-gate",
    "layout-framing-gate",
    "metal-stud-runbook",
    "shaftwall-gate",
    "fire-rated-assembly-gate",
    "acoustics-stc-gate",
    "inwall-cover-release",
    "board-hang-runbook",
    "taping-finish-gate",
    "weather-protect-gate",
    "interiors-closeout",
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
        return ["Proceed to next interiors sequence / workflow", "Keep UL/STC photos + in-wall release logs current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — secure scaffold; restore rated barriers / egress",
            "Preserve assembly photos, UL refs, timestamps",
            "Re-enter through pre-interiors-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "interiors-lead"]
    return [
        "Do not hang board / tape / close rated walls",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.materials = MaterialsSubmittalAgent()
        self.layout = LayoutControlAgent()
        self.framing = MetalStudFramingAgent()
        self.shaft = ShaftwallAgent()
        self.acoustics = AcousticsStcAgent()
        self.fire = FireRatedAssembliesAgent()
        self.blocking = BlockingBackingAgent()
        self.board = BoardHangAgent()
        self.finish = TapingFinishAgent()
        self.openings = OpeningsDoorsAgent()
        self.inwall = InwallCoverReleaseAgent()
        self.weather = WeatherProtectAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = InteriorsLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_interiors_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.materials.evaluate(ctx),
            self.layout.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-interiors-gate", ctx, gates, {
            "GO": "Pre-interiors clear — framing may proceed.",
            "HOLD": "Pre-interiors holding — materials/layout/environment.",
            "ABORT": "Pre-interiors aborted by fail-safe.",
        })

    def layout_framing_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.layout.evaluate(ctx), self.openings.evaluate(ctx), self.qa.evaluate(ctx, phase="pre")]
        return self._finish("layout-framing-gate", ctx, gates, {
            "GO": "Layout/framing control clear.",
            "HOLD": "Layout holding.",
            "ABORT": "Layout aborted.",
        })

    def metal_stud_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.framing.evaluate(ctx),
            self.blocking.evaluate(ctx),
            self.layout.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("metal-stud-runbook", ctx, gates, {
            "GO": "Metal stud framing clear.",
            "HOLD": "Metal stud holding.",
            "ABORT": "Metal stud aborted.",
        })

    def shaftwall_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "shaftwall": {**(ctx.get("shaftwall") or {}), "required": True},
               "fire_rated": {**(ctx.get("fire_rated") or {}), "required": True}}
        gates = [
            self.shaft.evaluate(ctx),
            self.fire.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("shaftwall-gate", ctx, gates, {
            "GO": "Shaftwall clear.",
            "HOLD": "Shaftwall holding.",
            "ABORT": "Shaftwall aborted — restore rated barrier.",
        })

    def fire_rated_assembly_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "fire_rated": {**(ctx.get("fire_rated") or {}), "required": True}}
        gates = [
            self.fire.evaluate(ctx),
            self.shaft.evaluate(ctx),
            self.openings.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("fire-rated-assembly-gate", ctx, gates, {
            "GO": "Fire-rated assembly clear.",
            "HOLD": "Fire-rated assembly holding.",
            "ABORT": "Fire-rated assembly aborted.",
        })

    def acoustics_stc_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "acoustics": {**(ctx.get("acoustics") or {}), "required": True}}
        gates = [
            self.acoustics.evaluate(ctx),
            self.framing.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("acoustics-stc-gate", ctx, gates, {
            "GO": "Acoustics/STC clear.",
            "HOLD": "Acoustics holding.",
            "ABORT": "Acoustics aborted.",
        })

    def inwall_cover_release(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.inwall.evaluate(ctx),
            self.blocking.evaluate(ctx),
            self.fire.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("inwall-cover-release", ctx, gates, {
            "GO": "In-wall cover release clear — board may hang.",
            "HOLD": "In-wall cover holding.",
            "ABORT": "In-wall cover aborted.",
        })

    def board_hang_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.inwall.evaluate(ctx),
            self.board.evaluate(ctx),
            self.materials.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("board-hang-runbook", ctx, gates, {
            "GO": "Board hang clear.",
            "HOLD": "Board hang holding.",
            "ABORT": "Board hang aborted.",
        })

    def taping_finish_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.finish.evaluate(ctx),
            self.board.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("taping-finish-gate", ctx, gates, {
            "GO": "Taping/finish clear.",
            "HOLD": "Taping/finish holding.",
            "ABORT": "Taping/finish aborted.",
        })

    def weather_protect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-protect-gate", ctx, gates, {
            "GO": "Environment clear.",
            "HOLD": "Environment holding.",
            "ABORT": "Environment aborted.",
        })

    def interiors_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="closeout"),
            self.fire.evaluate(ctx),
            self.acoustics.evaluate(ctx),
            self.finish.evaluate(ctx),
            self.openings.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("interiors-closeout", ctx, gates, {
            "GO": "Interiors closeout clear.",
            "HOLD": "Interiors closeout holding.",
            "ABORT": "Interiors closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "interiors-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "superintendent")},
        )]
        summary = "ABORT escalated — stop work and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
