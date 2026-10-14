"""Named Commissioning workflow runners."""
from __future__ import annotations
from typing import Any, Callable
from modules.commissioning_swarm.agents import (
    CalibrationAgent, CrewOpsAgent, CxLeadAgent, CxPlanAgent, FunctionalTestAgent,
    IssuesPunchAgent, LifeSafetyCxAgent, OmTrainingAgent, PerformanceTolAgent,
    PrefunctionalAgent, QaInspectorAgent, SafetyFailsafeAgent, SeasonalDeferredAgent,
    StartupSafeAgent, TabBalanceAgent, WitnessSignoffAgent,
)
from modules.commissioning_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-cx-gate", "prefunctional-gate", "startup-gate", "tab-gate",
    "functional-test-gate", "witness-signoff-gate", "performance-gate",
    "calibration-gate", "life-safety-cx-gate", "om-training-gate",
    "cx-closeout", "hold-abort",
)

def _decide(gates):
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.status == "FAIL" for g in active): return "ABORT"
    if any(g.status in ("FAIL", "HOLD") for g in active): return "HOLD"
    return "GO"

def _actions(decision, gates):
    if decision == "GO":
        return ["Proceed to next Cx milestone under plan", "Keep logs, witnesses, and issue tracker current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP acceptance — do not sign systems over",
            "Preserve test logs, witness sheets, TAB/Cx reports, timestamps",
            "Re-enter through pre-cx-gate or functional-test-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "cx-lead"]
    return ["Do not accept Cx milestone until cleared",
            *[f"Clear {g.agent}: {g.detail}" for g in holds],
            "Re-run failed gates + safety-failsafe before release"]

def _id(ctx):
    return ctx.get("zone_id") or ctx.get("system_id") or ctx.get("area") or "ZONE-UNSET"

class WorkflowRunner:
    def __init__(self):
        self.plan = CxPlanAgent(); self.pf = PrefunctionalAgent()
        self.startup = StartupSafeAgent(); self.tab = TabBalanceAgent()
        self.func = FunctionalTestAgent(); self.witness = WitnessSignoffAgent()
        self.cal = CalibrationAgent(); self.perf = PerformanceTolAgent()
        self.issues = IssuesPunchAgent(); self.om = OmTrainingAgent()
        self.seasonal = SeasonalDeferredAgent(); self.life = LifeSafetyCxAgent()
        self.safety = SafetyFailsafeAgent(); self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent(); self.lead = CxLeadAgent()

    def _finish(self, workflow, ctx, gates, summaries):
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_cx_gate(self, ctx):
        gates = [self.plan.evaluate(ctx), self.pf.evaluate(ctx), self.crew.evaluate(ctx, True),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "pre")]
        return self._finish("pre-cx-gate", ctx, gates, {
            "GO": "Pre-Cx clear — prefunctional/startup path may proceed.",
            "HOLD": "Pre-Cx holding — plan/PF/crew.",
            "ABORT": "Pre-Cx aborted by fail-safe.",
        })

    def prefunctional_gate(self, ctx):
        gates = [self.pf.evaluate(ctx), self.issues.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("prefunctional-gate", ctx, gates, {
            "GO": "Prefunctional clear.", "HOLD": "Prefunctional holding.", "ABORT": "Prefunctional aborted.",
        })

    def startup_gate(self, ctx):
        gates = [self.startup.evaluate(ctx), self.pf.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("startup-gate", ctx, gates, {
            "GO": "Startup clear.", "HOLD": "Startup holding.", "ABORT": "Startup aborted — unsafe energize.",
        })

    def tab_gate(self, ctx):
        gates = [self.tab.evaluate(ctx), self.cal.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("tab-gate", ctx, gates, {
            "GO": "TAB clear.", "HOLD": "TAB holding.", "ABORT": "TAB aborted.",
        })

    def functional_test_gate(self, ctx):
        gates = [self.func.evaluate(ctx), self.witness.evaluate(ctx), self.perf.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("functional-test-gate", ctx, gates, {
            "GO": "Functional tests clear.", "HOLD": "Functional tests holding.",
            "ABORT": "Functional tests aborted — invalid/failed.",
        })

    def witness_signoff_gate(self, ctx):
        gates = [self.witness.evaluate(ctx), self.func.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("witness-signoff-gate", ctx, gates, {
            "GO": "Witness sign-off clear.", "HOLD": "Witness holding.", "ABORT": "Witness aborted — invalid result.",
        })

    def performance_gate(self, ctx):
        gates = [self.perf.evaluate(ctx), self.cal.evaluate(ctx), self.tab.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("performance-gate", ctx, gates, {
            "GO": "Performance clear.", "HOLD": "Performance holding.",
            "ABORT": "Performance aborted — retest required.",
        })

    def calibration_gate(self, ctx):
        gates = [self.cal.evaluate(ctx), self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("calibration-gate", ctx, gates, {
            "GO": "Calibration clear.", "HOLD": "Calibration holding.", "ABORT": "Calibration aborted.",
        })

    def life_safety_cx_gate(self, ctx):
        ctx = {**ctx, "life_safety": {**(ctx.get("life_safety") or {}), "required": True}}
        gates = [self.life.evaluate(ctx), self.func.evaluate(ctx), self.witness.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("life-safety-cx-gate", ctx, gates, {
            "GO": "Life-safety Cx clear.", "HOLD": "Life-safety Cx holding.",
            "ABORT": "Life-safety Cx aborted.",
        })

    def om_training_gate(self, ctx):
        gates = [self.om.evaluate(ctx), self.issues.evaluate(ctx), self.seasonal.evaluate(ctx),
                 self.qa.evaluate(ctx, "during")]
        return self._finish("om-training-gate", ctx, gates, {
            "GO": "O&M/training clear.", "HOLD": "O&M/training holding.", "ABORT": "O&M/training aborted.",
        })

    def cx_closeout(self, ctx):
        gates = [self.qa.evaluate(ctx, "closeout"), self.witness.evaluate(ctx), self.om.evaluate(ctx),
                 self.issues.evaluate(ctx), self.seasonal.evaluate(ctx), self.crew.evaluate(ctx, False)]
        return self._finish("cx-closeout", ctx, gates, {
            "GO": "Cx closeout clear.", "HOLD": "Cx closeout holding.", "ABORT": "Cx closeout aborted.",
        })

    def hold_abort(self, ctx):
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult("cx-lead", "FAIL" if decision == "ABORT" else "HOLD", reason,
                            {"owner": ctx.get("owner", "cxa")})]
        summary = "ABORT escalated — stop Cx acceptance." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))

def get_workflow_handlers(runner=None):
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
