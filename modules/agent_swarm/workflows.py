"""Named repeatable workflow runners for the ConcreteOps crew swarm."""

from __future__ import annotations

from typing import Any, Callable

from modules.agent_swarm.agents import (
    CrewOpsAgent,
    MaterialsMixAgent,
    PourLeadAgent,
    QCInspectorAgent,
    SafetyFailsafeAgent,
    WeatherGateAgent,
)
from modules.agent_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-pour-gate",
    "pour-day-runbook",
    "mid-pour-monitor",
    "post-pour-closeout",
    "crew-briefing",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in gates):
        return "ABORT"
    if any(g.status in ("FAIL", "HOLD") for g in gates):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next workflow step", "Keep mid-pour monitor on cadence"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK immediately and secure the deck",
            "Preserve tickets, readings, photos, timestamps",
            "Re-enter only through pre-pour-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD")]
    return [
        "Do not start/continue placement",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


class WorkflowRunner:
    def __init__(self) -> None:
        self.materials = MaterialsMixAgent()
        self.weather = WeatherGateAgent()
        self.qc = QCInspectorAgent()
        self.crew = CrewOpsAgent()
        self.safety = SafetyFailsafeAgent()
        self.pour_lead = PourLeadAgent()

    def pre_pour_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.materials.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qc.evaluate(ctx, phase="pre"),
            self.crew.evaluate(ctx, require_briefing=True),
            self.safety.evaluate(ctx),
        ]
        gates.append(self.pour_lead.assemble(ctx, gates, "pre-pour-gate"))
        decision = _decide(gates)
        summary = {
            "GO": "All pre-pour gates clear — trucks may roll.",
            "HOLD": "Pre-pour gate holding — clear blockers before placement.",
            "ABORT": "Pre-pour aborted by fail-safe — stop and escalate.",
        }[decision]
        return SwarmResult("pre-pour-gate", ctx.get("pour_id", "UNKNOWN"), decision, summary, gates, _actions(decision, gates))

    def pour_day_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        if not ctx.get("pre_pour_go"):
            pre = self.pre_pour_gate(ctx)
            if pre.decision != "GO":
                pre.workflow = "pour-day-runbook"
                pre.summary = "Pour-day blocked — pre-pour gate is not GO."
                return pre

        gates = [
            self.crew.evaluate(ctx, require_briefing=True),
            self.qc.evaluate(ctx, phase="during"),
            self.weather.evaluate(ctx),
            self.safety.evaluate({**ctx, "require_telemetry": True}),
        ]
        gates.append(self.pour_lead.assemble(ctx, gates, "pour-day-runbook"))
        decision = _decide(gates)
        summary = {
            "GO": "Pour-day runbook clear — continue placement per zone plan.",
            "HOLD": "Pour-day holding — pause placement until gates clear.",
            "ABORT": "Pour-day aborted — execute stop-work protocol.",
        }[decision]
        return SwarmResult("pour-day-runbook", ctx.get("pour_id", "UNKNOWN"), decision, summary, gates, _actions(decision, gates))

    def mid_pour_monitor(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qc.evaluate(ctx, phase="during"),
            self.weather.evaluate(ctx),
            self.safety.evaluate({**ctx, "require_telemetry": True}),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        gates.append(self.pour_lead.assemble(ctx, gates, "mid-pour-monitor"))
        decision = _decide(gates)
        summary = {
            "GO": "Mid-pour health check clear — continue.",
            "HOLD": "Mid-pour hold — slow or pause until cleared.",
            "ABORT": "Mid-pour abort — stop placement now.",
        }[decision]
        return SwarmResult("mid-pour-monitor", ctx.get("pour_id", "UNKNOWN"), decision, summary, gates, _actions(decision, gates))

    def post_pour_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            GateResult(
                "pour-lead",
                "PASS" if ctx.get("pour_completed") else "HOLD",
                (
                    f"Closeout yards={ctx.get('volume_cy')} exceptions={len(ctx.get('exceptions') or [])}"
                    if ctx.get("pour_completed")
                    else "Pour not marked completed"
                ),
                {"exceptions": ctx.get("exceptions") or []},
            ),
            self.qc.evaluate(ctx, phase="post"),
            self.crew.evaluate({**ctx, "crew": {**(ctx.get("crew") or {}), "briefing_complete": True}}, require_briefing=False),
            self.materials.evaluate(ctx) if ctx.get("mix") else GateResult("materials-mix", "HOLD", "Ticket reconciliation missing", {}),
            self.safety.evaluate(ctx),
        ]
        decision = _decide(gates)
        summary = {
            "GO": "Closeout packet complete — curing owner assigned.",
            "HOLD": "Closeout incomplete — finish packet items.",
            "ABORT": "Closeout blocked by residual fail-safe hazard.",
        }[decision]
        actions = _actions(decision, gates)
        if decision == "GO":
            actions = [
                f"Curing owner: {(ctx.get('curing') or {}).get('owner', 'unassigned')}",
                "File closeout packet to document control",
                *actions,
            ]
        return SwarmResult("post-pour-closeout", ctx.get("pour_id", "UNKNOWN"), decision, summary, gates, actions)

    def crew_briefing(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.crew.run_briefing(ctx),
            self.weather.evaluate(ctx) if ctx.get("weather") else GateResult("weather-gate", "ADVISORY", "Briefing without live weather — use advisory protocol", {}),
            GateResult(
                "pour-lead",
                "PASS",
                f"Briefing facts for {ctx.get('pour_id', 'UNKNOWN')} / {ctx.get('area', 'area TBD')}",
                {},
            ),
        ]
        decision: Decision = "GO" if gates[0].status == "PASS" else "HOLD"
        summary = "Crew briefing complete." if decision == "GO" else "Crew briefing incomplete."
        actions = (
            ["Proceed to pre-pour-gate"]
            if decision == "GO"
            else [f"Cover missing briefing items: {gates[0].evidence.get('missing')}"]
        )
        return SwarmResult("crew-briefing", ctx.get("pour_id", "UNKNOWN"), decision, summary, gates, actions)

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        reason = ctx.get("block_reason") or "unspecified gate failure"
        severity = (ctx.get("severity") or "HOLD").upper()
        if severity not in ("HOLD", "ABORT"):
            severity = "HOLD"
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        gates = [
            GateResult(
                "safety-failsafe" if decision == "ABORT" else "pour-lead",
                "FAIL" if decision == "ABORT" else "HOLD",
                reason,
                {"owner": ctx.get("owner", "superintendent")},
            )
        ]
        summary = (
            "ABORT escalated — stop-work and preserve evidence."
            if decision == "ABORT"
            else "HOLD escalated — clear owner action then re-check."
        )
        return SwarmResult("hold-abort", ctx.get("pour_id", "UNKNOWN"), decision, summary, gates, _actions(decision, gates))


RunnerFn = Callable[[dict[str, Any]], SwarmResult]


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, RunnerFn]:
    r = runner or WorkflowRunner()
    return {
        "pre-pour-gate": r.pre_pour_gate,
        "pour-day-runbook": r.pour_day_runbook,
        "mid-pour-monitor": r.mid_pour_monitor,
        "post-pour-closeout": r.post_pour_closeout,
        "crew-briefing": r.crew_briefing,
        "hold-abort": r.hold_abort,
    }
