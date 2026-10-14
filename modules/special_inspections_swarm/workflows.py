"""Named special inspections workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.special_inspections_swarm.agents import (
    AgencyCredentialsAgent,
    ConcreteSiAgent,
    CrewOpsAgent,
    FinalReportAgent,
    FireResistanceSiAgent,
    HoldPointReleaseAgent,
    ItpSchedulerAgent,
    MasonrySiAgent,
    NdtTestingAgent,
    NonconformanceAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SiLeadAgent,
    SoilsFoundationSiAgent,
    StatementOfSiAgent,
    SteelSiAgent,
)
from modules.special_inspections_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-si-program-gate",
    "daily-si-dispatch",
    "soils-foundation-hold",
    "concrete-pour-si-gate",
    "steel-connection-si-gate",
    "masonry-grout-si-gate",
    "fireproofing-si-gate",
    "ndt-release-gate",
    "cover-before-si-gate",
    "ncr-disposition-gate",
    "si-final-report",
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
        return ["Proceed to next SI / trade hold point", "File daily SI report + photos"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — do not cover; expose if already covered without SI",
            "Preserve hold-point IDs, photos, agency notes, timestamps",
            "Re-enter through pre-si-program-gate / cover-before-si-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "si-lead"]
    return [
        "Do not pour / cover / fireproof / grout until SI clears",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("hold_point") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.sossi = StatementOfSiAgent()
        self.schedule = ItpSchedulerAgent()
        self.soils = SoilsFoundationSiAgent()
        self.concrete = ConcreteSiAgent()
        self.steel = SteelSiAgent()
        self.masonry = MasonrySiAgent()
        self.fire = FireResistanceSiAgent()
        self.ndt = NdtTestingAgent()
        self.agency = AgencyCredentialsAgent()
        self.release = HoldPointReleaseAgent()
        self.ncr = NonconformanceAgent()
        self.final = FinalReportAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = SiLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_si_program_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.sossi.evaluate(ctx),
            self.agency.evaluate(ctx),
            self.schedule.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-si-program-gate", ctx, gates, {
            "GO": "SI program clear — hold points may be dispatched.",
            "HOLD": "SI program holding — SOSSI/agency/schedule.",
            "ABORT": "SI program aborted by fail-safe.",
        })

    def daily_si_dispatch(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.schedule.evaluate(ctx),
            self.agency.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("daily-si-dispatch", ctx, gates, {
            "GO": "Daily SI dispatch clear.",
            "HOLD": "Daily SI dispatch holding.",
            "ABORT": "Daily SI dispatch aborted.",
        })

    def soils_foundation_hold(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "soils_si": {**(ctx.get("soils_si") or {}), "required": True}}
        gates = [
            self.soils.evaluate(ctx),
            self.release.evaluate(ctx),
            self.ncr.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("soils-foundation-hold", ctx, gates, {
            "GO": "Soils/foundation SI hold clear.",
            "HOLD": "Soils/foundation SI holding.",
            "ABORT": "Soils/foundation SI aborted.",
        })

    def concrete_pour_si_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "concrete_si": {**(ctx.get("concrete_si") or {}), "required": True}}
        gates = [
            self.concrete.evaluate(ctx),
            self.release.evaluate(ctx),
            self.agency.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("concrete-pour-si-gate", ctx, gates, {
            "GO": "Concrete pour SI clear.",
            "HOLD": "Concrete pour SI holding.",
            "ABORT": "Concrete pour SI aborted.",
        })

    def steel_connection_si_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "steel_si": {**(ctx.get("steel_si") or {}), "required": True}}
        gates = [
            self.steel.evaluate(ctx),
            self.ndt.evaluate(ctx),
            self.release.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("steel-connection-si-gate", ctx, gates, {
            "GO": "Steel connection SI clear.",
            "HOLD": "Steel connection SI holding.",
            "ABORT": "Steel connection SI aborted.",
        })

    def masonry_grout_si_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "masonry_si": {**(ctx.get("masonry_si") or {}), "required": True}}
        gates = [
            self.masonry.evaluate(ctx),
            self.release.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("masonry-grout-si-gate", ctx, gates, {
            "GO": "Masonry grout SI clear.",
            "HOLD": "Masonry grout SI holding.",
            "ABORT": "Masonry grout SI aborted.",
        })

    def fireproofing_si_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "fire_si": {**(ctx.get("fire_si") or {}), "required": True}}
        gates = [
            self.fire.evaluate(ctx),
            self.release.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("fireproofing-si-gate", ctx, gates, {
            "GO": "Fireproofing SI clear.",
            "HOLD": "Fireproofing SI holding.",
            "ABORT": "Fireproofing SI aborted.",
        })

    def ndt_release_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.ndt.evaluate(ctx),
            self.steel.evaluate(ctx),
            self.ncr.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("ndt-release-gate", ctx, gates, {
            "GO": "NDT release clear.",
            "HOLD": "NDT release holding.",
            "ABORT": "NDT release aborted.",
        })

    def cover_before_si_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.release.evaluate(ctx),
            self.ncr.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("cover-before-si-gate", ctx, gates, {
            "GO": "Cover/next trade authorized after SI.",
            "HOLD": "Cover holding — SI release incomplete.",
            "ABORT": "Cover aborted — do not conceal.",
        })

    def ncr_disposition_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.ncr.evaluate(ctx),
            self.release.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("ncr-disposition-gate", ctx, gates, {
            "GO": "SI NCR disposition clear.",
            "HOLD": "SI NCR disposition holding.",
            "ABORT": "SI NCR disposition aborted.",
        })

    def si_final_report(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.final.evaluate(ctx),
            self.ncr.evaluate(ctx),
            self.sossi.evaluate(ctx),
            self.agency.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("si-final-report", ctx, gates, {
            "GO": "Final SI report clear.",
            "HOLD": "Final SI report holding.",
            "ABORT": "Final SI report aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "si-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "si_agency_pm")},
        )]
        summary = "ABORT escalated — stop work; do not cover." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
