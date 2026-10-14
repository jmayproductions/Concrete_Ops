"""Named CoreProof lab workflow runners."""
from __future__ import annotations
from typing import Any, Callable
from modules.coreproof_swarm.agents import (
    BreakScheduleAgent, CastHandlingAgent, CoreAstm42Agent, CrewOpsAgent,
    CylinderAstm39Agent, FieldVsLabAgent, FlexuralBeamAgent, HandlingDeviationAgent,
    InitialCureAgent, LabLeadAgent, MoistLabCureAgent, QaInspectorAgent,
    SafetyFailsafeAgent, SampleIdAgent, StrengthComplianceAgent, TransportLabAgent,
)
from modules.coreproof_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-sample-gate", "cast-handling-gate", "transport-lab-gate", "moist-cure-gate",
    "break-schedule-gate", "cylinder-break-gate", "core-test-gate",
    "strength-compliance-gate", "field-vs-lab-gate", "low-strength-abort",
    "lab-closeout", "hold-abort",
)

def _decide(gates):
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.status == "FAIL" for g in active): return "ABORT"
    if any(g.status in ("FAIL", "HOLD") for g in active): return "HOLD"
    return "GO"

def _actions(decision, gates):
    if decision == "GO":
        return ["Proceed with sampling/lab plan", "Keep chain-of-custody and temp logs current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP acceptance — do not rely on invalid/failing strengths",
            "Notify structural engineer; preserve samples, tickets, photos, timestamps",
            "Re-enter through pre-sample-gate or core-test-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "lab-lead"]
    return ["Do not accept placement strength until cleared",
            *[f"Clear {g.agent}: {g.detail}" for g in holds],
            "Re-run failed gates + safety-failsafe before release"]

def _id(ctx):
    return ctx.get("zone_id") or (ctx.get("sample") or {}).get("sample_id") or ctx.get("area") or "ZONE-UNSET"

class WorkflowRunner:
    def __init__(self):
        self.sample = SampleIdAgent(); self.cast = CastHandlingAgent()
        self.initial = InitialCureAgent(); self.transport = TransportLabAgent()
        self.moist = MoistLabCureAgent(); self.break_sched = BreakScheduleAgent()
        self.cylinder = CylinderAstm39Agent(); self.core = CoreAstm42Agent()
        self.flex = FlexuralBeamAgent(); self.strength = StrengthComplianceAgent()
        self.fieldlab = FieldVsLabAgent(); self.handling = HandlingDeviationAgent()
        self.safety = SafetyFailsafeAgent(); self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent(); self.lead = LabLeadAgent()

    def _finish(self, workflow, ctx, gates, summaries):
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_sample_gate(self, ctx):
        gates = [self.sample.evaluate(ctx), self.cast.evaluate(ctx), self.initial.evaluate(ctx),
                 self.crew.evaluate(ctx, True), self.safety.evaluate(ctx), self.qa.evaluate(ctx, "pre")]
        return self._finish("pre-sample-gate", ctx, gates, {
            "GO": "Pre-sample clear — casting/sampling may proceed.",
            "HOLD": "Pre-sample holding — ID/cast/initial cure.",
            "ABORT": "Pre-sample aborted by fail-safe.",
        })

    def cast_handling_gate(self, ctx):
        gates = [self.cast.evaluate(ctx), self.sample.evaluate(ctx), self.handling.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("cast-handling-gate", ctx, gates, {
            "GO": "Cast handling clear.", "HOLD": "Cast handling holding.", "ABORT": "Cast handling aborted.",
        })

    def transport_lab_gate(self, ctx):
        gates = [self.transport.evaluate(ctx), self.sample.evaluate(ctx), self.handling.evaluate(ctx),
                 self.qa.evaluate(ctx, "during")]
        return self._finish("transport-lab-gate", ctx, gates, {
            "GO": "Transport clear.", "HOLD": "Transport holding.", "ABORT": "Transport aborted.",
        })

    def moist_cure_gate(self, ctx):
        gates = [self.moist.evaluate(ctx), self.initial.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("moist-cure-gate", ctx, gates, {
            "GO": "Moist lab cure clear.", "HOLD": "Moist lab cure holding.", "ABORT": "Moist lab cure aborted.",
        })

    def break_schedule_gate(self, ctx):
        gates = [self.break_sched.evaluate(ctx), self.sample.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("break-schedule-gate", ctx, gates, {
            "GO": "Break schedule clear.", "HOLD": "Break schedule holding.", "ABORT": "Break schedule aborted.",
        })

    def cylinder_break_gate(self, ctx):
        ctx = {**ctx, "cylinder": {**(ctx.get("cylinder") or {}), "required": True}}
        gates = [self.cylinder.evaluate(ctx), self.break_sched.evaluate(ctx), self.strength.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "report")]
        return self._finish("cylinder-break-gate", ctx, gates, {
            "GO": "Cylinder break clear.", "HOLD": "Cylinder break holding.",
            "ABORT": "Cylinder break aborted — strength fail-safe.",
        })

    def core_test_gate(self, ctx):
        ctx = {**ctx, "core": {**(ctx.get("core") or {}), "required": True, "tested": True}}
        gates = [self.core.evaluate(ctx), self.strength.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "report")]
        return self._finish("core-test-gate", ctx, gates, {
            "GO": "Core test clear.", "HOLD": "Core test holding.",
            "ABORT": "Core test aborted — rejection criteria met.",
        })

    def strength_compliance_gate(self, ctx):
        gates = [self.strength.evaluate(ctx), self.cylinder.evaluate(ctx), self.fieldlab.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "report")]
        return self._finish("strength-compliance-gate", ctx, gates, {
            "GO": "Strength compliance clear.", "HOLD": "Strength compliance holding.",
            "ABORT": "Strength compliance aborted.",
        })

    def field_vs_lab_gate(self, ctx):
        ctx = {**ctx, "field_lab": {**(ctx.get("field_lab") or {}), "required": True}}
        gates = [self.fieldlab.evaluate(ctx), self.strength.evaluate(ctx), self.qa.evaluate(ctx, "report")]
        return self._finish("field-vs-lab-gate", ctx, gates, {
            "GO": "Field vs lab clear.", "HOLD": "Field vs lab holding.", "ABORT": "Field vs lab aborted.",
        })

    def low_strength_abort(self, ctx):
        gates = [self.strength.evaluate(ctx), self.core.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "report")]
        return self._finish("low-strength-abort", ctx, gates, {
            "GO": "Low-strength path clear (no abort conditions).",
            "HOLD": "Low-strength path holding for review.",
            "ABORT": "Low-strength aborted — engineer / rejection path.",
        })

    def lab_closeout(self, ctx):
        gates = [self.qa.evaluate(ctx, "report"), self.strength.evaluate(ctx),
                 self.sample.evaluate(ctx), self.crew.evaluate(ctx, False)]
        return self._finish("lab-closeout", ctx, gates, {
            "GO": "Lab closeout clear.", "HOLD": "Lab closeout holding.", "ABORT": "Lab closeout aborted.",
        })

    def hold_abort(self, ctx):
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult("lab-lead", "FAIL" if decision == "ABORT" else "HOLD", reason,
                            {"owner": ctx.get("owner", "lab_manager")})]
        summary = "ABORT escalated — stop acceptance and notify engineer." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))

def get_workflow_handlers(runner=None):
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
