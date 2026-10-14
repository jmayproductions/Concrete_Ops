"""Named Life Safety workflow runners."""
from __future__ import annotations
from typing import Any
from modules.life_safety_swarm.agents import (
    CrewOpsAgent, DoorHardwareAgent, DoorScheduleAgent, EgressLightingAgent, EgressPathAgent,
    ExitSignageAgent, FireAlarmAgent, FireDoorAgent, LsLeadAgent, PunchTrackerAgent,
    QaInspectorAgent, SafetyFailsafeAgent, SmokeDamperAgent, SprinklerHydroAgent,
    StairGuardAgent, TcoReadinessAgent,
)
from modules.life_safety_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-ls-gate", "egress-path-gate", "exit-signage-gate", "egress-lighting-gate",
    "door-hardware-gate", "fire-door-gate", "sprinkler-hydro-gate", "fire-alarm-gate",
    "smoke-damper-gate", "punch-walk-gate", "tco-readiness", "hold-abort",
)

def _decide(gates):
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.status == "FAIL" for g in active): return "ABORT"
    if any(g.status in ("FAIL", "HOLD") for g in active): return "HOLD"
    return "GO"

def _actions(decision, gates):
    if decision == "GO":
        return ["Proceed to next life-safety milestone", "Keep door sheets, test logs, and punch tracker current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP — do not claim TCO / do not cover or occupy",
            "Preserve door sheets, alarm/sprinkler logs, photos, timestamps",
            "Re-enter through pre-ls-gate or failed gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "ls-lead"]
    return ["Do not accept LS milestone until cleared",
            *[f"Clear {g.agent}: {g.detail}" for g in holds],
            "Re-run failed gates + safety-failsafe before release"]

def _id(ctx):
    return ctx.get("zone_id") or ctx.get("floor_id") or ctx.get("area") or "ZONE-UNSET"

class WorkflowRunner:
    def __init__(self):
        self.egress = EgressPathAgent(); self.signs = ExitSignageAgent()
        self.lights = EgressLightingAgent(); self.stairs = StairGuardAgent()
        self.schedule = DoorScheduleAgent(); self.hardware = DoorHardwareAgent()
        self.firedoor = FireDoorAgent(); self.sprinkler = SprinklerHydroAgent()
        self.alarm = FireAlarmAgent(); self.damper = SmokeDamperAgent()
        self.punch = PunchTrackerAgent(); self.tco = TcoReadinessAgent()
        self.safety = SafetyFailsafeAgent(); self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent(); self.lead = LsLeadAgent()

    def _finish(self, workflow, ctx, gates, summaries):
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_ls_gate(self, ctx):
        gates = [self.egress.evaluate(ctx), self.signs.evaluate(ctx), self.schedule.evaluate(ctx),
                 self.crew.evaluate(ctx, True), self.safety.evaluate(ctx), self.qa.evaluate(ctx, "pre")]
        return self._finish("pre-ls-gate", ctx, gates, {
            "GO": "Pre-LS clear — egress/doors path may proceed.",
            "HOLD": "Pre-LS holding — egress/schedule/crew.",
            "ABORT": "Pre-LS aborted by fail-safe.",
        })

    def egress_path_gate(self, ctx):
        gates = [self.egress.evaluate(ctx), self.stairs.evaluate(ctx), self.signs.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("egress-path-gate", ctx, gates, {
            "GO": "Egress path clear.", "HOLD": "Egress path holding.", "ABORT": "Egress path aborted — blocked.",
        })

    def exit_signage_gate(self, ctx):
        gates = [self.signs.evaluate(ctx), self.lights.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("exit-signage-gate", ctx, gates, {
            "GO": "Exit signage clear.", "HOLD": "Exit signage holding.", "ABORT": "Exit signage aborted.",
        })

    def egress_lighting_gate(self, ctx):
        gates = [self.lights.evaluate(ctx), self.signs.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("egress-lighting-gate", ctx, gates, {
            "GO": "Egress lighting clear.", "HOLD": "Egress lighting holding.",
            "ABORT": "Egress lighting aborted — emergency-power fail.",
        })

    def door_hardware_gate(self, ctx):
        gates = [self.schedule.evaluate(ctx), self.hardware.evaluate(ctx), self.firedoor.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("door-hardware-gate", ctx, gates, {
            "GO": "Door hardware clear.", "HOLD": "Door hardware holding.", "ABORT": "Door hardware aborted — fire door.",
        })

    def fire_door_gate(self, ctx):
        gates = [self.firedoor.evaluate(ctx), self.hardware.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("fire-door-gate", ctx, gates, {
            "GO": "Fire door clear.", "HOLD": "Fire door holding.", "ABORT": "Fire door aborted.",
        })

    def sprinkler_hydro_gate(self, ctx):
        gates = [self.sprinkler.evaluate(ctx), self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("sprinkler-hydro-gate", ctx, gates, {
            "GO": "Sprinkler hydro clear.", "HOLD": "Sprinkler hydro holding.", "ABORT": "Sprinkler hydro aborted.",
        })

    def fire_alarm_gate(self, ctx):
        gates = [self.alarm.evaluate(ctx), self.lights.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("fire-alarm-gate", ctx, gates, {
            "GO": "Fire alarm clear.", "HOLD": "Fire alarm holding.", "ABORT": "Fire alarm aborted.",
        })

    def smoke_damper_gate(self, ctx):
        gates = [self.damper.evaluate(ctx), self.alarm.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("smoke-damper-gate", ctx, gates, {
            "GO": "Smoke dampers clear.", "HOLD": "Smoke dampers holding.", "ABORT": "Smoke dampers aborted.",
        })

    def punch_walk_gate(self, ctx):
        gates = [self.punch.evaluate(ctx), self.hardware.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("punch-walk-gate", ctx, gates, {
            "GO": "Punch walk clear.", "HOLD": "Punch walk holding.", "ABORT": "Punch walk aborted.",
        })

    def tco_readiness(self, ctx):
        gates = [self.tco.evaluate(ctx), self.egress.evaluate(ctx), self.lights.evaluate(ctx),
                 self.alarm.evaluate(ctx), self.sprinkler.evaluate(ctx), self.punch.evaluate(ctx),
                 self.qa.evaluate(ctx, "tco"), self.crew.evaluate(ctx, False)]
        return self._finish("tco-readiness", ctx, gates, {
            "GO": "TCO readiness clear.", "HOLD": "TCO readiness holding.", "ABORT": "TCO readiness aborted.",
        })

    def hold_abort(self, ctx):
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult("ls-lead", "FAIL" if decision == "ABORT" else "HOLD", reason,
                            {"owner": ctx.get("owner", "ls_lead")})]
        summary = "ABORT escalated — stop LS/TCO acceptance." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))

def get_workflow_handlers(runner=None):
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
