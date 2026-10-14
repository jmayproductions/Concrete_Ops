"""Named structural steel erection workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.steel_swarm.agents import (
    BoltingAgent,
    CoatingsAgent,
    CraneLogisticsAgent,
    CrewOpsAgent,
    DeckingAgent,
    ErectLeadAgent,
    FabMillAgent,
    FireproofingAgent,
    GroutBaseplateAgent,
    PlumbAlignmentAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SurveyAnchorsAgent,
    TempBracingAgent,
    WeatherGateAgent,
    WeldingAgent,
)
from modules.steel_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-erect-gate",
    "delivery-piece-gate",
    "anchor-baseplate-gate",
    "level-erect-runbook",
    "column-beam-pick",
    "bolting-qa",
    "welding-ndt-gate",
    "bracing-stability-lock",
    "plumb-alignment-check",
    "decking-release",
    "level-closeout",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status == "FAIL" and g.agent != "erect-lead" for g in active):
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            return "ABORT"
        return "HOLD"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next sequenced pick / workflow", "Maintain bracing + QA logs"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP PICKS — secure unstable members",
            "Preserve piece marks, torque/weld logs, photos, timestamps",
            "Re-enter only through pre-erect-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "erect-lead"]
    return [
        "Do not advance erection sequence",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("erect_id") or ctx.get("level") or "ERECT-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.fab = FabMillAgent()
        self.anchors = SurveyAnchorsAgent()
        self.crane = CraneLogisticsAgent()
        self.bracing = TempBracingAgent()
        self.bolting = BoltingAgent()
        self.welding = WeldingAgent()
        self.plumb = PlumbAlignmentAgent()
        self.decking = DeckingAgent()
        self.fire = FireproofingAgent()
        self.coatings = CoatingsAgent()
        self.grout = GroutBaseplateAgent()
        self.weather = WeatherGateAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = ErectLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        if any(g.status == "FAIL" and g.agent != "safety-failsafe" for g in gates):
            for g in gates:
                if g.status == "FAIL" and g.agent in {"temp-bracing", "bolting", "welding", "survey-anchors"}:
                    if not any(x.agent == "safety-failsafe" and x.status == "FAIL" for x in gates):
                        gates.append(GateResult("safety-failsafe", "FAIL", g.detail, g.evidence))
                    break
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_erect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.fab.evaluate(ctx),
            self.anchors.evaluate(ctx),
            self.crane.evaluate(ctx),
            self.bracing.plan(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish(
            "pre-erect-gate",
            ctx,
            gates,
            {
                "GO": "Pre-erect clear — steel picks may begin.",
                "HOLD": "Pre-erect holding — clear fab/anchors/crane/bracing/crew.",
                "ABORT": "Pre-erect aborted by fail-safe.",
            },
        )

    def delivery_piece_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.fab.evaluate(ctx),
            self.crane.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "delivery-piece-gate",
            ctx,
            gates,
            {
                "GO": "Delivery clear — piece marks/heat numbers OK.",
                "HOLD": "Delivery holding — piece marks/heat numbers/logistics.",
                "ABORT": "Delivery aborted by fail-safe.",
            },
        )

    def anchor_baseplate_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.anchors.evaluate(ctx),
            self.grout.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "anchor-baseplate-gate",
            ctx,
            gates,
            {
                "GO": "Anchors/baseplates released for columns.",
                "HOLD": "Anchor/baseplate holding.",
                "ABORT": "Anchor gate aborted.",
            },
        )

    def level_erect_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        if not ctx.get("pre_erect_go"):
            pre = self.pre_erect_gate(ctx)
            if pre.decision != "GO":
                pre.workflow = "level-erect-runbook"
                pre.summary = "Level erect blocked — pre-erect gate is not GO."
                return pre
        gates = [
            self.bracing.lock_in(ctx) if (ctx.get("bracing") or {}).get("braces_installed") is not None else self.bracing.plan(ctx),
            self.bolting.evaluate(ctx),
            self.welding.evaluate(ctx),
            self.plumb.evaluate(ctx),
            self.decking.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "level-erect-runbook",
            ctx,
            gates,
            {
                "GO": "Level erect clear — continue sequence.",
                "HOLD": "Level erect holding — braces/bolts/welds/plumb.",
                "ABORT": "Level erect aborted — stop picks and secure.",
            },
        )

    def column_beam_pick(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.crane.evaluate(ctx),
            self.bracing.plan(ctx),
            self.bolting.evaluate(ctx),
            self.plumb.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "column-beam-pick",
            ctx,
            gates,
            {
                "GO": "Column/beam pick clear.",
                "HOLD": "Pick holding.",
                "ABORT": "Pick aborted.",
            },
        )

    def bolting_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.bolting.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "bolting-qa",
            ctx,
            gates,
            {
                "GO": "Bolting QA clear.",
                "HOLD": "Bolting holding.",
                "ABORT": "Bolting aborted.",
            },
        )

    def welding_ndt_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.welding.evaluate({**ctx, "require_welding": True}),
            self.qa.evaluate(ctx, phase="during"),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "welding-ndt-gate",
            ctx,
            gates,
            {
                "GO": "Welding/NDT clear.",
                "HOLD": "Welding holding.",
                "ABORT": "Welding aborted.",
            },
        )

    def bracing_stability_lock(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.bracing.lock_in(ctx),
            self.bolting.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "bracing-stability-lock",
            ctx,
            gates,
            {
                "GO": "Stability locked — level may advance.",
                "HOLD": "Stability not locked.",
                "ABORT": "Stability abort — unstable frame.",
            },
        )

    def plumb_alignment_check(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.plumb.evaluate(ctx),
            self.anchors.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish(
            "plumb-alignment-check",
            ctx,
            gates,
            {
                "GO": "Plumb/alignment clear.",
                "HOLD": "Alignment holding.",
                "ABORT": "Alignment aborted.",
            },
        )

    def decking_release(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.decking.evaluate({**ctx, "require_decking": True}),
            self.plumb.evaluate(ctx),
            self.bolting.evaluate(ctx),
            self.bracing.lock_in(ctx) if (ctx.get("bracing") or {}).get("braces_installed") is not None else self.bracing.plan(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "decking-release",
            ctx,
            gates,
            {
                "GO": "Decking released.",
                "HOLD": "Decking holding.",
                "ABORT": "Decking aborted.",
            },
        )

    def level_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="post"),
            self.bolting.evaluate(ctx),
            self.welding.evaluate(ctx),
            self.plumb.evaluate(ctx),
            self.coatings.evaluate(ctx),
            self.fire.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish(
            "level-closeout",
            ctx,
            gates,
            {
                "GO": "Level closeout complete.",
                "HOLD": "Level closeout incomplete.",
                "ABORT": "Level closeout aborted.",
            },
        )

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        reason = ctx.get("block_reason") or "unspecified gate failure"
        severity = (ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        gates = [
            GateResult(
                "safety-failsafe" if decision == "ABORT" else "erect-lead",
                "FAIL" if decision == "ABORT" else "HOLD",
                reason,
                {"owner": ctx.get("owner", "superintendent")},
            )
        ]
        summary = (
            "ABORT escalated — stop picks and secure."
            if decision == "ABORT"
            else "HOLD escalated — clear owner action then re-check."
        )
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


RunnerFn = Callable[[dict[str, Any]], SwarmResult]


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, RunnerFn]:
    r = runner or WorkflowRunner()
    return {
        "pre-erect-gate": r.pre_erect_gate,
        "delivery-piece-gate": r.delivery_piece_gate,
        "anchor-baseplate-gate": r.anchor_baseplate_gate,
        "level-erect-runbook": r.level_erect_runbook,
        "column-beam-pick": r.column_beam_pick,
        "bolting-qa": r.bolting_qa,
        "welding-ndt-gate": r.welding_ndt_gate,
        "bracing-stability-lock": r.bracing_stability_lock,
        "plumb-alignment-check": r.plumb_alignment_check,
        "decking-release": r.decking_release,
        "level-closeout": r.level_closeout,
        "hold-abort": r.hold_abort,
    }
