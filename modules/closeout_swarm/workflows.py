"""Named closeout / punch / turnover workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.closeout_swarm.agents import (
    AhjTcoAgent,
    AsbuiltsOmAgent,
    CloseoutLeadAgent,
    CommissioningAgent,
    CrewOpsAgent,
    DoorHardwareAgent,
    FinishesQaAgent,
    FireProtectionAgent,
    LifeSafetyAgent,
    NcrCloseoutAgent,
    PunchlistAgent,
    QaInspectorAgent,
    RoomReadinessAgent,
    SafetyFailsafeAgent,
    SignatureChainAgent,
    TurnoverPackageAgent,
)
from modules.closeout_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-closeout-gate",
    "room-readiness-gate",
    "punchlist-walk",
    "life-safety-gate",
    "door-hardware-qa",
    "finishes-punch-gate",
    "fire-protection-closeout",
    "commissioning-gate",
    "ncr-closeout-gate",
    "tco-readiness-gate",
    "turnover-package-gate",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status == "FAIL" and g.agent != "closeout-lead" for g in active):
        # life-safety/FP FAIL promotes via safety agent typically; otherwise HOLD
        return "HOLD"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next closeout sequence / workflow", "Keep punch tracker + archive current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "NO OCCUPY / NO HANDOFF — secure life-safety issues",
            "Preserve photos, test reports, punch/NCR logs, signatures",
            "Re-enter through pre-closeout-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "closeout-lead"]
    return [
        "Do not release TCO or client turnover",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.rooms = RoomReadinessAgent()
        self.punch = PunchlistAgent()
        self.life = LifeSafetyAgent()
        self.doors = DoorHardwareAgent()
        self.finishes = FinishesQaAgent()
        self.fp = FireProtectionAgent()
        self.cx = CommissioningAgent()
        self.ncr = NcrCloseoutAgent()
        self.docs = AsbuiltsOmAgent()
        self.turnover = TurnoverPackageAgent()
        self.sigs = SignatureChainAgent()
        self.tco = AhjTcoAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = CloseoutLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        # Promote life-safety/FP FAIL into safety abort when occupy/handoff workflows
        if workflow in {"life-safety-gate", "tco-readiness-gate", "turnover-package-gate"}:
            for g in list(gates):
                if g.status == "FAIL" and g.agent in {"life-safety", "fire-protection"}:
                    if not any(x.agent == "safety-failsafe" and x.status == "FAIL" for x in gates):
                        gates.append(GateResult("safety-failsafe", "FAIL", g.detail, g.evidence))
                    break
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_closeout_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.rooms.evaluate(ctx),
            self.punch.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-closeout-gate", ctx, gates, {
            "GO": "Pre-closeout clear — punch/TCO sequence may proceed.",
            "HOLD": "Pre-closeout holding — rooms/punch/crew.",
            "ABORT": "Pre-closeout aborted by fail-safe.",
        })

    def room_readiness_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.rooms.evaluate(ctx), self.finishes.evaluate(ctx), self.qa.evaluate(ctx, phase="pre")]
        return self._finish("room-readiness-gate", ctx, gates, {
            "GO": "Room readiness clear.",
            "HOLD": "Room readiness holding.",
            "ABORT": "Room readiness aborted.",
        })

    def punchlist_walk(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.punch.evaluate(ctx),
            self.rooms.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("punchlist-walk", ctx, gates, {
            "GO": "Punchlist walk clear.",
            "HOLD": "Punchlist holding.",
            "ABORT": "Punchlist aborted.",
        })

    def life_safety_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.life.evaluate(ctx),
            self.doors.evaluate({**ctx, "require_doors": True}),
            self.fp.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("life-safety-gate", ctx, gates, {
            "GO": "Life safety clear.",
            "HOLD": "Life safety holding.",
            "ABORT": "Life safety aborted — no occupy.",
        })

    def door_hardware_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.doors.evaluate({**ctx, "require_doors": True}),
            self.life.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("door-hardware-qa", ctx, gates, {
            "GO": "Door/hardware QA clear.",
            "HOLD": "Door/hardware holding.",
            "ABORT": "Door/hardware aborted.",
        })

    def finishes_punch_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.finishes.evaluate({**ctx, "require_finishes": True}),
            self.punch.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("finishes-punch-gate", ctx, gates, {
            "GO": "Finishes punch clear.",
            "HOLD": "Finishes holding.",
            "ABORT": "Finishes aborted.",
        })

    def fire_protection_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.fp.evaluate(ctx),
            self.cx.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("fire-protection-closeout", ctx, gates, {
            "GO": "Fire protection closeout clear.",
            "HOLD": "Fire protection holding.",
            "ABORT": "Fire protection aborted.",
        })

    def commissioning_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.cx.evaluate({**ctx, "commissioning": {**(ctx.get("commissioning") or {}), "required": True}}),
            self.docs.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
        ]
        return self._finish("commissioning-gate", ctx, gates, {
            "GO": "Commissioning/TAB clear.",
            "HOLD": "Commissioning holding.",
            "ABORT": "Commissioning aborted.",
        })

    def ncr_closeout_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.ncr.evaluate(ctx),
            self.punch.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("ncr-closeout-gate", ctx, gates, {
            "GO": "NCR closeout clear.",
            "HOLD": "NCR closeout holding.",
            "ABORT": "NCR closeout aborted.",
        })

    def tco_readiness_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.tco.evaluate(ctx),
            self.life.evaluate(ctx),
            self.fp.evaluate(ctx),
            self.ncr.evaluate(ctx),
            self.sigs.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
        ]
        return self._finish("tco-readiness-gate", ctx, gates, {
            "GO": "TCO readiness clear.",
            "HOLD": "TCO holding.",
            "ABORT": "TCO aborted — no occupy.",
        })

    def turnover_package_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.turnover.evaluate(ctx),
            self.docs.evaluate(ctx),
            self.sigs.evaluate(ctx),
            self.ncr.evaluate(ctx),
            self.cx.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("turnover-package-gate", ctx, gates, {
            "GO": "Turnover package clear for client handoff.",
            "HOLD": "Turnover package holding.",
            "ABORT": "Turnover aborted — no handoff.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        reason = ctx.get("block_reason") or "unspecified gate failure"
        severity = (ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        gates = [GateResult(
            "safety-failsafe" if decision == "ABORT" else "closeout-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "project_manager")},
        )]
        summary = "ABORT escalated — no occupy/handoff." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
