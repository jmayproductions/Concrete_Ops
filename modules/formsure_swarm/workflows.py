"""Named FormSure formwork workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.formsure_swarm.agents import (
    BracingLateralAgent,
    CrewOpsAgent,
    FormLeadAgent,
    FormPressureAgent,
    FormSystemAgent,
    LeakSealAgent,
    LoadTransferAgent,
    PanelAlignmentAgent,
    PanelReuseAgent,
    PourDropAgent,
    QaInspectorAgent,
    ReleaseAgentAgent,
    SafetyFailsafeAgent,
    ShoringPropsAgent,
    StripTimingAgent,
    TieRodsAgent,
)
from modules.formsure_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-pour-form-gate",
    "form-erect-gate",
    "release-agent-check",
    "tie-brace-gate",
    "scc-leak-gate",
    "pour-drop-gate",
    "form-pressure-gate",
    "shore-stability-gate",
    "strip-readiness-gate",
    "load-transfer-gate",
    "post-strip-closeout",
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
        return ["Proceed under form design / pour-rate controls", "Re-check ties, braces, and shores before and during pour"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP POUR/STRIP — secure forms, shores, and exclusion",
            "Preserve checklists, strength proofs, photos, timestamps",
            "Re-enter through pre-pour-form-gate or strip-readiness-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "form-lead"]
    return [
        "Do not pour or strip until cleared",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("element_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.system = FormSystemAgent()
        self.align = PanelAlignmentAgent()
        self.release = ReleaseAgentAgent()
        self.ties = TieRodsAgent()
        self.bracing = BracingLateralAgent()
        self.leak = LeakSealAgent()
        self.drop = PourDropAgent()
        self.pressure = FormPressureAgent()
        self.shores = ShoringPropsAgent()
        self.strip = StripTimingAgent()
        self.load = LoadTransferAgent()
        self.panels = PanelReuseAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = FormLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_pour_form_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.system.evaluate(ctx),
            self.align.evaluate(ctx),
            self.release.evaluate(ctx),
            self.ties.evaluate(ctx),
            self.bracing.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-pour-form-gate", ctx, gates, {
            "GO": "Pre-pour forms clear — placement may proceed under rate/drop controls.",
            "HOLD": "Pre-pour form holding — system/align/ties/braces/release.",
            "ABORT": "Pre-pour form aborted by fail-safe.",
        })

    def form_erect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.system.evaluate(ctx),
            self.align.evaluate(ctx),
            self.bracing.evaluate(ctx),
            self.shores.evaluate(ctx),
            self.qa.evaluate(ctx, phase="erect"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("form-erect-gate", ctx, gates, {
            "GO": "Form erect clear.",
            "HOLD": "Form erect holding.",
            "ABORT": "Form erect aborted.",
        })

    def release_agent_check(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.release.evaluate(ctx),
            self.panels.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("release-agent-check", ctx, gates, {
            "GO": "Release agent check clear.",
            "HOLD": "Release agent holding.",
            "ABORT": "Release agent aborted.",
        })

    def tie_brace_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.ties.evaluate(ctx),
            self.bracing.evaluate(ctx),
            self.pressure.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("tie-brace-gate", ctx, gates, {
            "GO": "Ties and braces clear.",
            "HOLD": "Ties/braces holding.",
            "ABORT": "Ties/braces aborted — do not pour.",
        })

    def scc_leak_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        mix = {**(ctx.get("mix") or {}), "type": (ctx.get("mix") or {}).get("type") or "scc"}
        ctx = {**ctx, "mix": mix}
        gates = [
            self.leak.evaluate(ctx),
            self.release.evaluate(ctx),
            self.ties.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("scc-leak-gate", ctx, gates, {
            "GO": "SCC leak seals clear.",
            "HOLD": "SCC leak holding.",
            "ABORT": "SCC leak aborted.",
        })

    def pour_drop_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.drop.evaluate(ctx),
            self.system.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("pour-drop-gate", ctx, gates, {
            "GO": "Pour drop height clear.",
            "HOLD": "Pour drop holding.",
            "ABORT": "Pour drop aborted — use chute/tremie or lower free fall.",
        })

    def form_pressure_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.pressure.evaluate(ctx),
            self.ties.evaluate(ctx),
            self.bracing.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("form-pressure-gate", ctx, gates, {
            "GO": "Form pressure clear.",
            "HOLD": "Form pressure holding.",
            "ABORT": "Form pressure aborted — slow/stop pour.",
        })

    def shore_stability_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.shores.evaluate(ctx),
            self.load.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("shore-stability-gate", ctx, gates, {
            "GO": "Shore stability clear.",
            "HOLD": "Shore stability holding.",
            "ABORT": "Shore stability aborted.",
        })

    def strip_readiness_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        strip = {**(ctx.get("strip") or {}), "required": True}
        ctx = {**ctx, "strip": strip}
        gates = [
            self.strip.evaluate(ctx),
            self.load.evaluate(ctx),
            self.shores.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="strip"),
        ]
        return self._finish("strip-readiness-gate", ctx, gates, {
            "GO": "Strip readiness clear.",
            "HOLD": "Strip readiness holding.",
            "ABORT": "Strip aborted — premature or unsafe release.",
        })

    def load_transfer_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.load.evaluate(ctx),
            self.strip.evaluate(ctx),
            self.shores.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="strip"),
        ]
        return self._finish("load-transfer-gate", ctx, gates, {
            "GO": "Load transfer clear.",
            "HOLD": "Load transfer holding.",
            "ABORT": "Load transfer aborted.",
        })

    def post_strip_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="strip"),
            self.panels.evaluate(ctx),
            self.strip.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("post-strip-closeout", ctx, gates, {
            "GO": "Post-strip closeout clear.",
            "HOLD": "Post-strip closeout holding.",
            "ABORT": "Post-strip closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "form-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "form_superintendent")},
        )]
        summary = "ABORT escalated — stop pour/strip and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
