"""Named MEP rough-in + firestop workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.mep_swarm.agents import (
    ClashCoordAgent,
    CrewOpsAgent,
    DamperLifeSafetyAgent,
    ElectricalRoughAgent,
    FirestopAgent,
    HvacRoughAgent,
    InsulationHangersAgent,
    LabelingAsbuiltAgent,
    MepLeadAgent,
    PlumbingRoughAgent,
    PressureTestAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    ShaftAccessAgent,
    SleevePenetrationAgent,
    WeatherGateAgent,
)
from modules.mep_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-mep-gate",
    "clash-sleeve-gate",
    "hvac-rough-runbook",
    "electrical-rough-runbook",
    "plumbing-rough-runbook",
    "firestop-precover-gate",
    "damper-life-safety-gate",
    "shaft-inspection-gate",
    "pressure-test-gate",
    "inwall-cover-release",
    "mep-closeout",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status == "FAIL" and g.agent != "mep-lead" for g in active):
        return "HOLD"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next MEP sequence / workflow", "Maintain firestop photos + test logs"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — do not cover / energize / enter uncontrolled shafts",
            "Preserve photos, UL tags, pressure charts, timestamps",
            "Re-enter through pre-mep-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "mep-lead"]
    return [
        "Do not cover walls/ceilings or backfill shafts",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.clash = ClashCoordAgent()
        self.sleeves = SleevePenetrationAgent()
        self.hvac = HvacRoughAgent()
        self.elec = ElectricalRoughAgent()
        self.plum = PlumbingRoughAgent()
        self.fire = FirestopAgent()
        self.dampers = DamperLifeSafetyAgent()
        self.shaft = ShaftAccessAgent()
        self.pressure = PressureTestAgent()
        self.insul = InsulationHangersAgent()
        self.labels = LabelingAsbuiltAgent()
        self.weather = WeatherGateAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = MepLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_mep_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.clash.evaluate(ctx),
            self.sleeves.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-mep-gate", ctx, gates, {
            "GO": "Pre-MEP clear — rough-in may begin.",
            "HOLD": "Pre-MEP holding — clash/sleeves/crew.",
            "ABORT": "Pre-MEP aborted by fail-safe.",
        })

    def clash_sleeve_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.clash.evaluate(ctx), self.sleeves.evaluate(ctx), self.qa.evaluate(ctx, phase="pre"), self.safety.evaluate(ctx)]
        return self._finish("clash-sleeve-gate", ctx, gates, {
            "GO": "Clash/sleeve gate clear.",
            "HOLD": "Clash/sleeve holding.",
            "ABORT": "Clash/sleeve aborted.",
        })

    def hvac_rough_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.hvac.evaluate({**ctx, "require_hvac": True}),
            self.insul.evaluate(ctx),
            self.dampers.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("hvac-rough-runbook", ctx, gates, {
            "GO": "HVAC rough clear.",
            "HOLD": "HVAC rough holding.",
            "ABORT": "HVAC aborted.",
        })

    def electrical_rough_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.elec.evaluate({**ctx, "require_electrical": True}),
            self.labels.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("electrical-rough-runbook", ctx, gates, {
            "GO": "Electrical rough clear.",
            "HOLD": "Electrical holding.",
            "ABORT": "Electrical aborted.",
        })

    def plumbing_rough_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.plum.evaluate({**ctx, "require_plumbing": True}),
            self.pressure.evaluate(ctx),
            self.insul.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("plumbing-rough-runbook", ctx, gates, {
            "GO": "Plumbing rough clear.",
            "HOLD": "Plumbing holding.",
            "ABORT": "Plumbing aborted.",
        })

    def firestop_precover_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.fire.evaluate(ctx),
            self.sleeves.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("firestop-precover-gate", ctx, gates, {
            "GO": "Firestop pre-cover clear.",
            "HOLD": "Firestop holding — no cover.",
            "ABORT": "Firestop aborted.",
        })

    def damper_life_safety_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.dampers.evaluate({**ctx, "require_dampers": True}),
            self.hvac.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("damper-life-safety-gate", ctx, gates, {
            "GO": "Damper/life-safety clear.",
            "HOLD": "Dampers holding.",
            "ABORT": "Dampers aborted.",
        })

    def shaft_inspection_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.shaft.evaluate({**ctx, "require_shaft": True}),
            self.clash.evaluate(ctx),
            self.fire.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("shaft-inspection-gate", ctx, gates, {
            "GO": "Shaft inspection clear.",
            "HOLD": "Shaft holding.",
            "ABORT": "Shaft aborted.",
        })

    def pressure_test_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.pressure.evaluate(ctx),
            self.plum.evaluate(ctx),
            self.hvac.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
        ]
        return self._finish("pressure-test-gate", ctx, gates, {
            "GO": "Pressure/DALT tests clear.",
            "HOLD": "Pressure tests holding/failed.",
            "ABORT": "Pressure tests aborted.",
        })

    def inwall_cover_release(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.clash.evaluate(ctx),
            self.fire.evaluate(ctx),
            self.hvac.evaluate({**ctx, "require_hvac": True}),
            self.elec.evaluate({**ctx, "require_electrical": True}),
            self.plum.evaluate({**ctx, "require_plumbing": True}),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("inwall-cover-release", ctx, gates, {
            "GO": "In-wall cover released.",
            "HOLD": "Cover blocked — clash/firestop/trades.",
            "ABORT": "Cover release aborted.",
        })

    def mep_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="post"),
            self.fire.evaluate(ctx),
            self.pressure.evaluate(ctx),
            self.labels.evaluate(ctx),
            self.dampers.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("mep-closeout", ctx, gates, {
            "GO": "MEP closeout complete.",
            "HOLD": "MEP closeout incomplete.",
            "ABORT": "MEP closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        reason = ctx.get("block_reason") or "unspecified gate failure"
        severity = (ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        gates = [GateResult(
            "safety-failsafe" if decision == "ABORT" else "mep-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "superintendent")},
        )]
        summary = "ABORT escalated — stop work and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
