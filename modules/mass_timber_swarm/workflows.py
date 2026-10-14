"""Named mass timber erection workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.mass_timber_swarm.agents import (
    AssemblySystemsAgent,
    ConnectionsAgent,
    CraneLogisticsAgent,
    CrewOpsAgent,
    ErectLeadAgent,
    FinishProtectAgent,
    GlulamFrameAgent,
    HybridInterfaceAgent,
    MoistureProtectAgent,
    PanelErectAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SupplyChainAgent,
    SurveyToleranceAgent,
    TempBracingAgent,
    WeatherGateAgent,
)
from modules.mass_timber_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-erect-gate",
    "delivery-jit-gate",
    "level-erect-runbook",
    "panel-placement",
    "glulam-frame-erect",
    "bracing-diaphragm-lock",
    "moisture-daily-check",
    "connection-qa",
    "hybrid-interface-gate",
    "topping-release",
    "level-closeout",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status == "FAIL" and g.agent != "erect-lead" for g in active):
        # non-safety FAILs hold unless safety already aborted
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            return "ABORT"
        return "HOLD"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next sequenced pick / workflow", "Maintain moisture + finish protection"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP PICKS — secure unstable members",
            "Preserve piece marks, photos, MC logs, timestamps",
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
        self.supply = SupplyChainAgent()
        self.survey = SurveyToleranceAgent()
        self.crane = CraneLogisticsAgent()
        self.moisture = MoistureProtectAgent()
        self.connections = ConnectionsAgent()
        self.bracing = TempBracingAgent()
        self.panels = PanelErectAgent()
        self.glulam = GlulamFrameAgent()
        self.hybrid = HybridInterfaceAgent()
        self.weather = WeatherGateAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.assembly = AssemblySystemsAgent()
        self.finish = FinishProtectAgent()
        self.qa = QaInspectorAgent()
        self.lead = ErectLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        if any(g.status == "FAIL" and g.agent != "safety-failsafe" for g in gates):
            # promote structural fails
            for g in gates:
                if g.status == "FAIL" and g.agent in {"temp-bracing", "connections", "survey-tolerance"}:
                    if not any(x.agent == "safety-failsafe" and x.status == "FAIL" for x in gates):
                        gates.append(GateResult("safety-failsafe", "FAIL", g.detail, g.evidence))
                    break
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_erect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.supply.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.hybrid.evaluate(ctx),
            self.crane.evaluate(ctx),
            self.moisture.plan_ready(ctx),
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
                "GO": "Pre-erect clear — timber picks may begin.",
                "HOLD": "Pre-erect holding — clear drawings/survey/crane/moisture/bracing.",
                "ABORT": "Pre-erect aborted by fail-safe.",
            },
        )

    def delivery_jit_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.supply.evaluate(ctx),
            self.crane.evaluate(ctx),
            self.moisture.plan_ready(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "delivery-jit-gate",
            ctx,
            gates,
            {
                "GO": "JIT delivery clear — trailer-direct picks OK.",
                "HOLD": "Delivery holding — piece marks/logistics/weather.",
                "ABORT": "Delivery aborted by fail-safe.",
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
            self.bracing.plan(ctx),
            self.glulam.evaluate({**ctx, "require_glulam": bool(ctx.get("glulam"))}),
            self.panels.evaluate(ctx) if ctx.get("panels") else GateResult("panel-erect", "SKIP", "No panel scope", {}),
            self.connections.evaluate(ctx),
            self.bracing.lock_in(ctx),
            self.moisture.daily(ctx) if (ctx.get("moisture") or {}).get("moisture_content_pct") is not None else self.moisture.plan_ready(ctx),
            self.finish.evaluate(ctx),
            self.assembly.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "level-erect-runbook",
            ctx,
            gates,
            {
                "GO": "Level erect clear — continue sequence / lock diaphragm.",
                "HOLD": "Level erect holding — braces/connections/moisture/panels.",
                "ABORT": "Level erect aborted — stop picks and secure.",
            },
        )

    def panel_placement(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.panels.evaluate(ctx),
            self.connections.evaluate(ctx),
            self.moisture.plan_ready(ctx),
            self.finish.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "panel-placement",
            ctx,
            gates,
            {
                "GO": "Panel placement clear.",
                "HOLD": "Panel placement holding.",
                "ABORT": "Panel placement aborted.",
            },
        )

    def glulam_frame_erect(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.glulam.evaluate({**ctx, "require_glulam": True}),
            self.connections.evaluate(ctx),
            self.bracing.lock_in(ctx) if (ctx.get("bracing") or {}).get("braces_installed") is not None else self.bracing.plan(ctx),
            self.finish.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "glulam-frame-erect",
            ctx,
            gates,
            {
                "GO": "Glulam frame erect clear.",
                "HOLD": "Glulam frame holding.",
                "ABORT": "Glulam frame aborted.",
            },
        )

    def bracing_diaphragm_lock(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.bracing.lock_in(ctx),
            self.connections.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "bracing-diaphragm-lock",
            ctx,
            gates,
            {
                "GO": "Diaphragm locked — level may advance.",
                "HOLD": "Diaphragm/bracing not locked.",
                "ABORT": "Bracing abort — unstable frame.",
            },
        )

    def moisture_daily_check(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.moisture.daily(ctx),
            self.weather.evaluate(ctx),
            self.finish.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
        ]
        return self._finish(
            "moisture-daily-check",
            ctx,
            gates,
            {
                "GO": "Moisture daily check clear.",
                "HOLD": "Moisture holding — dry/protect before covering.",
                "ABORT": "Moisture aborted by fail-safe.",
            },
        )

    def connection_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.connections.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.assembly.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "connection-qa",
            ctx,
            gates,
            {
                "GO": "Connection QA clear.",
                "HOLD": "Connection QA holding.",
                "ABORT": "Connection QA aborted.",
            },
        )

    def hybrid_interface_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.survey.evaluate(ctx),
            self.hybrid.evaluate(ctx),
            self.supply.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "hybrid-interface-gate",
            ctx,
            gates,
            {
                "GO": "Hybrid interface released for timber.",
                "HOLD": "Hybrid interface holding.",
                "ABORT": "Hybrid interface aborted.",
            },
        )

    def topping_release(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.moisture.daily(ctx),
            self.assembly.evaluate({**ctx, "assembly": {**(ctx.get("assembly") or {}), "topping_requested": True}}),
            self.qa.evaluate(ctx, phase="post"),
            self.connections.evaluate(ctx),
        ]
        return self._finish(
            "topping-release",
            ctx,
            gates,
            {
                "GO": "Topping/membrane release GO.",
                "HOLD": "Topping release holding — MC/assembly/connections.",
                "ABORT": "Topping release aborted.",
            },
        )

    def level_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="post"),
            self.bracing.lock_in(ctx),
            self.moisture.daily(ctx) if (ctx.get("moisture") or {}).get("moisture_content_pct") is not None else self.moisture.plan_ready(ctx),
            self.finish.evaluate(ctx),
            self.assembly.evaluate(ctx),
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
        "delivery-jit-gate": r.delivery_jit_gate,
        "level-erect-runbook": r.level_erect_runbook,
        "panel-placement": r.panel_placement,
        "glulam-frame-erect": r.glulam_frame_erect,
        "bracing-diaphragm-lock": r.bracing_diaphragm_lock,
        "moisture-daily-check": r.moisture_daily_check,
        "connection-qa": r.connection_qa,
        "hybrid-interface-gate": r.hybrid_interface_gate,
        "topping-release": r.topping_release,
        "level-closeout": r.level_closeout,
        "hold-abort": r.hold_abort,
    }
