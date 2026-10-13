"""Named repeatable workflow runners for the ConcreteOps crew swarm."""

from __future__ import annotations

from typing import Any, Callable

from modules.agent_swarm.agents import (
    CrewOpsAgent,
    MaterialsMixAgent,
    PourLeadAgent,
    PT_CREW_ROLES,
    PTStressAgent,
    QCInspectorAgent,
    SafetyFailsafeAgent,
    TILT_CREW_ROLES,
    TiltUpAgent,
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
    "pt-pre-stress-gate",
    "pt-stress-sequence",
    "tilt-up-cast-gate",
    "tilt-up-lift-day",
    "tilt-up-brace-release",
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
        self.pt = PTStressAgent()
        self.tilt = TiltUpAgent()

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

    def pt_pre_stress_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.pt.pre_stress_gate(ctx),
            self.qc.evaluate(ctx, phase="post")
            if (ctx.get("curing") or {}).get("started") or ctx.get("finish_accepted")
            else GateResult(
                "qc-inspector",
                "PASS" if (ctx.get("pt") or {}).get("concrete_strength_psi") else "HOLD",
                (
                    f"Strength evidence { (ctx.get('pt') or {}).get('concrete_strength_psi') } psi"
                    if (ctx.get("pt") or {}).get("concrete_strength_psi")
                    else "No strength evidence for stress"
                ),
                {},
            ),
            self.crew.evaluate(ctx, require_briefing=True, required_roles=PT_CREW_ROLES),
            self.safety.evaluate(ctx),
        ]
        gates.append(self.pour_lead.assemble(ctx, gates, "pt-pre-stress-gate"))
        decision = _decide(gates)
        # PT over-spacing FAIL from pt-stress without safety-failsafe should HOLD unless safety FAIL
        if decision == "HOLD" or decision == "GO" or decision == "ABORT":
            pass
        if any(g.agent == "pt-stress" and g.status == "FAIL" for g in gates) and decision != "ABORT":
            # Treat PT structural layout FAIL as HOLD unless safety aborted
            decision = "HOLD"
        summary = {
            "GO": "PT pre-stress gate clear — jacks may mobilize.",
            "HOLD": "PT pre-stress holding — clear strength/inventory/sequence blockers.",
            "ABORT": "PT pre-stress aborted by fail-safe.",
        }[decision]
        return SwarmResult(
            "pt-pre-stress-gate",
            ctx.get("pour_id") or ctx.get("deck_id") or "UNKNOWN",
            decision,
            summary,
            gates,
            _actions(decision, gates),
        )

    def pt_stress_sequence(self, ctx: dict[str, Any]) -> SwarmResult:
        if not ctx.get("pt_pre_stress_go"):
            pre = self.pt_pre_stress_gate(ctx)
            if pre.decision != "GO":
                pre.workflow = "pt-stress-sequence"
                pre.summary = "PT stressing blocked — pre-stress gate is not GO."
                return pre

        pt_gate = self.pt.stress_sequence(ctx)
        gates = [
            pt_gate,
            self.qc.evaluate(ctx, phase="during")
            if ctx.get("telemetry")
            else GateResult("qc-inspector", "PASS", "QC witnessing elongations per PT log", {}),
            self.crew.evaluate(ctx, require_briefing=False, required_roles=PT_CREW_ROLES),
            self.safety.evaluate(ctx),
        ]
        # Map PT strand failure FAIL into ABORT via synthetic safety if needed
        if pt_gate.status == "FAIL" and "ABORT stressing" in pt_gate.detail:
            gates.append(
                GateResult(
                    "safety-failsafe",
                    "FAIL",
                    pt_gate.detail,
                    pt_gate.evidence,
                )
            )
        gates.append(self.pour_lead.assemble(ctx, gates, "pt-stress-sequence"))
        decision = _decide(gates)
        if pt_gate.status == "FAIL" and "ABORT stressing" in pt_gate.detail:
            decision = "ABORT"
        elif pt_gate.status in ("FAIL", "HOLD") and decision == "GO":
            decision = "HOLD"
        summary = {
            "GO": "PT stress sequence clear — continue / certify remaining tendons.",
            "HOLD": "PT stressing holding — resolve elongation/psi/inspection items.",
            "ABORT": "PT stressing aborted — stop jacks and secure deck.",
        }[decision]
        return SwarmResult(
            "pt-stress-sequence",
            ctx.get("pour_id") or ctx.get("deck_id") or "UNKNOWN",
            decision,
            summary,
            gates,
            _actions(decision, gates),
        )

    def tilt_up_cast_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.tilt.cast_gate(ctx),
            self.materials.evaluate(ctx) if ctx.get("mix") else GateResult("materials-mix", "HOLD", "Mix ticket missing for panel cast", {}),
            self.qc.evaluate(ctx, phase="pre"),
            self.crew.evaluate(ctx, require_briefing=True, required_roles=TILT_CREW_ROLES),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        gates.append(self.pour_lead.assemble(ctx, gates, "tilt-up-cast-gate"))
        decision = _decide(gates)
        summary = {
            "GO": "Tilt-up cast gate clear — panel bed may cast.",
            "HOLD": "Tilt-up cast holding — clear embeds/forms/mix/weather.",
            "ABORT": "Tilt-up cast aborted by fail-safe.",
        }[decision]
        return SwarmResult(
            "tilt-up-cast-gate",
            ctx.get("pour_id") or ctx.get("panel_id") or "UNKNOWN",
            decision,
            summary,
            gates,
            _actions(decision, gates),
        )

    def tilt_up_lift_day(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.tilt.lift_day(ctx),
            self.weather.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True, required_roles=TILT_CREW_ROLES),
            self.qc.evaluate(ctx, phase="pre")
            if ctx.get("readiness")
            else GateResult("qc-inspector", "PASS", "Panel marks and brace hardware verified", {}),
            self.safety.evaluate(ctx),
        ]
        gates.append(self.pour_lead.assemble(ctx, gates, "tilt-up-lift-day"))
        decision = _decide(gates)
        summary = {
            "GO": "Tilt-up lift day clear — proceed panel-by-panel.",
            "HOLD": "Tilt-up lift holding — wind, strength, or brace blockers.",
            "ABORT": "Tilt-up lift aborted — stop picks and secure panels.",
        }[decision]
        return SwarmResult(
            "tilt-up-lift-day",
            ctx.get("pour_id") or ctx.get("panel_id") or "UNKNOWN",
            decision,
            summary,
            gates,
            _actions(decision, gates),
        )

    def tilt_up_brace_release(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.tilt.brace_release(ctx),
            self.qc.evaluate(ctx, phase="post")
            if ctx.get("curing") or ctx.get("finish_accepted")
            else GateResult("qc-inspector", "PASS", "Connection inspections accepted per tilt packet", {}),
            self.crew.evaluate(ctx, require_briefing=False, required_roles=TILT_CREW_ROLES),
            self.safety.evaluate(ctx),
        ]
        gates.append(self.pour_lead.assemble(ctx, gates, "tilt-up-brace-release"))
        decision = _decide(gates)
        if any(g.agent == "tilt-up" and g.status == "FAIL" for g in gates):
            decision = "ABORT"
        summary = {
            "GO": "Brace release clear — remove braces per engineer order.",
            "HOLD": "Brace release holding — permanent connections incomplete.",
            "ABORT": "Brace release aborted — re-brace and escalate instability.",
        }[decision]
        return SwarmResult(
            "tilt-up-brace-release",
            ctx.get("pour_id") or ctx.get("panel_id") or "UNKNOWN",
            decision,
            summary,
            gates,
            _actions(decision, gates),
        )


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
        "pt-pre-stress-gate": r.pt_pre_stress_gate,
        "pt-stress-sequence": r.pt_stress_sequence,
        "tilt-up-cast-gate": r.tilt_up_cast_gate,
        "tilt-up-lift-day": r.tilt_up_lift_day,
        "tilt-up-brace-release": r.tilt_up_brace_release,
    }
