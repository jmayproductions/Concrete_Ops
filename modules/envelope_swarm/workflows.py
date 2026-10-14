"""Named envelope / waterproofing workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.envelope_swarm.agents import (
    AirBarrierTestAgent,
    BelowGradeWpAgent,
    CladdingRainscreenAgent,
    CrewOpsAgent,
    CurtainWallAgent,
    DrainageProtectionAgent,
    EnvelopeLeadAgent,
    FlashingPenetrationsAgent,
    QaInspectorAgent,
    RoofingMembraneAgent,
    SafetyFailsafeAgent,
    SealantsAgent,
    SubstratePrepAgent,
    WaterTestAgent,
    WeatherBarrierAgent,
    WeatherGateAgent,
)
from modules.envelope_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-envelope-gate",
    "substrate-ready-gate",
    "wrb-air-barrier-gate",
    "below-grade-wp-runbook",
    "roofing-membrane-runbook",
    "flashing-penetration-qa",
    "curtain-wall-install-gate",
    "cladding-rainscreen-gate",
    "water-test-gate",
    "air-barrier-test-gate",
    "envelope-closeout",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status == "FAIL" and g.agent != "envelope-lead" for g in active):
        return "HOLD" if not any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active) else "ABORT"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next envelope sequence / workflow", "Maintain photo log + protection"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — secure open edges / hot-work / unprotected WP",
            "Preserve photos, test reports, timestamps",
            "Re-enter through pre-envelope-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "envelope-lead"]
    return [
        "Do not cover or backfill",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.substrate = SubstratePrepAgent()
        self.wrb = WeatherBarrierAgent()
        self.below = BelowGradeWpAgent()
        self.roof = RoofingMembraneAgent()
        self.flash = FlashingPenetrationsAgent()
        self.cw = CurtainWallAgent()
        self.clad = CladdingRainscreenAgent()
        self.seal = SealantsAgent()
        self.water = WaterTestAgent()
        self.air = AirBarrierTestAgent()
        self.drain = DrainageProtectionAgent()
        self.weather = WeatherGateAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = EnvelopeLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        if any(g.status == "FAIL" and g.agent in {"roofing-membrane", "flashing-penetrations", "water-test", "below-grade-wp"} for g in gates):
            if not any(x.agent == "safety-failsafe" and x.status == "FAIL" for x in gates):
                # structural water fails stay HOLD unless safety also trips; promote only backfill/torch via safety agent
                pass
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        # water-test FAIL should HOLD unless safety FAIL; _decide already maps non-safety FAIL to HOLD
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_envelope_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.substrate.evaluate(ctx),
            self.wrb.evaluate({**ctx, "require_wrb": bool(ctx.get("wrb"))}),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-envelope-gate", ctx, gates, {
            "GO": "Pre-envelope clear — membrane/WRB work may begin.",
            "HOLD": "Pre-envelope holding — substrate/WRB/crew/weather.",
            "ABORT": "Pre-envelope aborted by fail-safe.",
        })

    def substrate_ready_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.substrate.evaluate(ctx), self.drain.evaluate(ctx), self.weather.evaluate(ctx), self.qa.evaluate(ctx, phase="pre")]
        return self._finish("substrate-ready-gate", ctx, gates, {
            "GO": "Substrate ready for membrane/WRB.",
            "HOLD": "Substrate holding.",
            "ABORT": "Substrate aborted.",
        })

    def wrb_air_barrier_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.wrb.evaluate({**ctx, "require_wrb": True}),
            self.flash.evaluate(ctx),
            self.seal.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("wrb-air-barrier-gate", ctx, gates, {
            "GO": "WRB/air barrier clear.",
            "HOLD": "WRB/air barrier holding.",
            "ABORT": "WRB aborted.",
        })

    def below_grade_wp_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.substrate.evaluate(ctx),
            self.below.evaluate({**ctx, "require_below_grade": True}),
            self.drain.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("below-grade-wp-runbook", ctx, gates, {
            "GO": "Below-grade WP clear for protection/backfill sequence.",
            "HOLD": "Below-grade WP holding.",
            "ABORT": "Below-grade WP aborted.",
        })

    def roofing_membrane_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.substrate.evaluate(ctx),
            self.roof.evaluate({**ctx, "require_roofing": True}),
            self.flash.evaluate(ctx),
            self.drain.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("roofing-membrane-runbook", ctx, gates, {
            "GO": "Roofing membrane clear.",
            "HOLD": "Roofing holding.",
            "ABORT": "Roofing aborted.",
        })

    def flashing_penetration_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.flash.evaluate(ctx), self.seal.evaluate(ctx), self.qa.evaluate(ctx, phase="during")]
        return self._finish("flashing-penetration-qa", ctx, gates, {
            "GO": "Flashing/penetration QA clear.",
            "HOLD": "Flashing holding.",
            "ABORT": "Flashing aborted.",
        })

    def curtain_wall_install_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.cw.evaluate({**ctx, "require_curtain_wall": True}),
            self.seal.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("curtain-wall-install-gate", ctx, gates, {
            "GO": "Curtain wall install clear.",
            "HOLD": "Curtain wall holding.",
            "ABORT": "Curtain wall aborted.",
        })

    def cladding_rainscreen_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.wrb.evaluate({**ctx, "require_wrb": True}),
            self.clad.evaluate({**ctx, "require_cladding": True}),
            self.flash.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("cladding-rainscreen-gate", ctx, gates, {
            "GO": "Cladding/rainscreen clear.",
            "HOLD": "Cladding holding.",
            "ABORT": "Cladding aborted.",
        })

    def water_test_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.water.evaluate(ctx),
            self.roof.evaluate(ctx),
            self.cw.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("water-test-gate", ctx, gates, {
            "GO": "Water test clear.",
            "HOLD": "Water test holding / failed — repair and retest.",
            "ABORT": "Water test aborted.",
        })

    def air_barrier_test_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.air.evaluate(ctx),
            self.wrb.evaluate({**ctx, "require_wrb": True}),
            self.seal.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
        ]
        return self._finish("air-barrier-test-gate", ctx, gates, {
            "GO": "Air barrier test clear.",
            "HOLD": "Air barrier holding.",
            "ABORT": "Air barrier aborted.",
        })

    def envelope_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="post"),
            self.water.evaluate(ctx),
            self.air.evaluate(ctx),
            self.clad.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("envelope-closeout", ctx, gates, {
            "GO": "Envelope closeout complete.",
            "HOLD": "Envelope closeout incomplete.",
            "ABORT": "Envelope closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        reason = ctx.get("block_reason") or "unspecified gate failure"
        severity = (ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        gates = [GateResult(
            "safety-failsafe" if decision == "ABORT" else "envelope-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "superintendent")},
        )]
        summary = "ABORT escalated — stop work and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {
        "pre-envelope-gate": r.pre_envelope_gate,
        "substrate-ready-gate": r.substrate_ready_gate,
        "wrb-air-barrier-gate": r.wrb_air_barrier_gate,
        "below-grade-wp-runbook": r.below_grade_wp_runbook,
        "roofing-membrane-runbook": r.roofing_membrane_runbook,
        "flashing-penetration-qa": r.flashing_penetration_qa,
        "curtain-wall-install-gate": r.curtain_wall_install_gate,
        "cladding-rainscreen-gate": r.cladding_rainscreen_gate,
        "water-test-gate": r.water_test_gate,
        "air-barrier-test-gate": r.air_barrier_test_gate,
        "envelope-closeout": r.envelope_closeout,
        "hold-abort": r.hold_abort,
    }
