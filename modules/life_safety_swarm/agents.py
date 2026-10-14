"""Deterministic specialist gates for Life Safety + Door Hardware."""
from __future__ import annotations
from typing import Any
from modules.life_safety_swarm.schemas import GateResult

ERECT_ROLES = ('ls_lead', 'door_tech', 'sprinkler_tech', 'alarm_tech', 'egress_inspector', 'qc_tech', 'safety_watch')

def _num(v, default=None):
    if v is None: return default
    try: return float(v)
    except (TypeError, ValueError): return default

class EgressPathAgent:
    name = "egress-path"
    def evaluate(self, ctx):
        e = ctx.get("egress") or {}
        if e.get("blocked") or e.get("discharge_blocked"):
            return GateResult(self.name, "FAIL", "Egress path or exit discharge blocked", {"egress": e})
        width = _num(e.get("clear_width_in"))
        if width is not None and width < 36:
            return GateResult(self.name, "HOLD", f"Clear width {width} in < 36 in minimum", {"egress": e})
        if e.get("clear") is False:
            return GateResult(self.name, "HOLD", "Egress path not verified clear", {"egress": e})
        return GateResult(self.name, "PASS", "Egress path clear", {"egress": e})

class ExitSignageAgent:
    name = "exit-signage"
    def evaluate(self, ctx):
        s = ctx.get("exit_signs") or {}
        if s.get("missing") or s.get("covered") or s.get("wrong_arrow"):
            return GateResult(self.name, "FAIL", "Exit signage missing/covered/wrong", {"exit_signs": s})
        if s.get("illuminated") is False or s.get("battery_backup") is False:
            return GateResult(self.name, "HOLD", "Exit signs not illuminated / no battery backup", {"exit_signs": s})
        return GateResult(self.name, "PASS", "Exit signage clear", {"exit_signs": s})

class EgressLightingAgent:
    name = "egress-lighting"
    def evaluate(self, ctx):
        l = ctx.get("egress_lighting") or {}
        if l.get("emergency_power_fail"):
            return GateResult(self.name, "FAIL", "Egress lighting failed emergency-power test", {"egress_lighting": l})
        if l.get("tested") is False:
            return GateResult(self.name, "HOLD", "Egress lighting not tested under emergency power", {"egress_lighting": l})
        return GateResult(self.name, "PASS", "Egress lighting clear", {"egress_lighting": l})

class StairGuardAgent:
    name = "stair-guard"
    def evaluate(self, ctx):
        s = ctx.get("stairs") or {}
        if s.get("required") is False:
            return GateResult(self.name, "SKIP", "Stairs N/A for this zone", {})
        variance = _num(s.get("riser_variance_in"))
        if variance is not None and variance > 0.1875:
            return GateResult(self.name, "HOLD", f"Riser variance {variance} in > 3/16 in", {"stairs": s})
        guard = _num(s.get("guard_height_in"))
        if guard is not None and guard < 42:
            return GateResult(self.name, "HOLD", f"Guardrail {guard} in < 42 in", {"stairs": s})
        if s.get("ok") is False:
            return GateResult(self.name, "HOLD", "Stairs/guards out of tolerance", {"stairs": s})
        return GateResult(self.name, "PASS", "Stairs/guards clear", {"stairs": s})

class DoorScheduleAgent:
    name = "door-schedule"
    def evaluate(self, ctx):
        d = ctx.get("door_schedule") or {}
        if d.get("mismatch"):
            return GateResult(self.name, "HOLD", "Door ID does not match schedule", {"door_schedule": d})
        if d.get("swing_wrong"):
            return GateResult(self.name, "HOLD", "Door swing direction incorrect vs code/schedule", {"door_schedule": d})
        return GateResult(self.name, "PASS", "Door schedule match clear", {"door_schedule": d})

class DoorHardwareAgent:
    name = "door-hardware"
    def evaluate(self, ctx):
        h = ctx.get("hardware") or {}
        if h.get("strike_misaligned") or h.get("wrong_function"):
            return GateResult(self.name, "HOLD", "Hardware misaligned or wrong function", {"hardware": h})
        if h.get("closer_ok") is False:
            return GateResult(self.name, "HOLD", "Closer/hold-open not functioning", {"hardware": h})
        if h.get("electrified_untested"):
            return GateResult(self.name, "HOLD", "Electrified hardware not tested", {"hardware": h})
        return GateResult(self.name, "PASS", "Door hardware clear", {"hardware": h})

class FireDoorAgent:
    name = "fire-door"
    def evaluate(self, ctx):
        f = ctx.get("fire_door") or {}
        if f.get("required") is False:
            return GateResult(self.name, "SKIP", "No rated doors in this run", {})
        if f.get("label_missing"):
            return GateResult(self.name, "FAIL", "Fire door label missing", {"fire_door": f})
        gap_side = _num(f.get("gap_side_in")); gap_bottom = _num(f.get("gap_bottom_in"))
        if gap_side is not None and gap_side > 0.125:
            return GateResult(self.name, "FAIL", f"Fire door side/head gap {gap_side} in > 1/8 in", {"fire_door": f})
        if gap_bottom is not None and gap_bottom > 0.75:
            return GateResult(self.name, "FAIL", f"Fire door bottom gap {gap_bottom} in > 3/4 in", {"fire_door": f})
        if f.get("seals_missing"):
            return GateResult(self.name, "FAIL", "Intumescent/smoke seals missing on rated door", {"fire_door": f})
        if f.get("failed") and not f.get("zone_reinspect"):
            return GateResult(self.name, "FAIL", "Failed fire door without zone re-inspection", {"fire_door": f})
        return GateResult(self.name, "PASS", "Fire door NFPA 80 clear", {"fire_door": f})

class SprinklerHydroAgent:
    name = "sprinkler-hydro"
    def evaluate(self, ctx):
        s = ctx.get("sprinkler") or {}
        if s.get("required") is False:
            return GateResult(self.name, "SKIP", "Sprinkler N/A", {})
        if s.get("uncapped_dry"):
            return GateResult(self.name, "FAIL", "Uncapped dry sprinkler — block cover/sign-off", {"sprinkler": s})
        if s.get("hydro_pass") is False:
            return GateResult(self.name, "FAIL", "Sprinkler hydrostatic test failed (need 200 psi / 2 hr)", {"sprinkler": s})
        if s.get("hydro_pass") is None and not s.get("tested"):
            return GateResult(self.name, "HOLD", "Sprinkler hydro not tested", {"sprinkler": s})
        return GateResult(self.name, "PASS", "Sprinkler hydro clear", {"sprinkler": s})

class FireAlarmAgent:
    name = "fire-alarm"
    def evaluate(self, ctx):
        a = ctx.get("fire_alarm") or {}
        if a.get("required") is False:
            return GateResult(self.name, "SKIP", "Fire alarm N/A", {})
        if a.get("function_pass") is False:
            return GateResult(self.name, "FAIL", "Fire alarm function test failed", {"fire_alarm": a})
        dba = _num(a.get("audible_dba"))
        if dba is not None and dba < 75:
            return GateResult(self.name, "FAIL", f"Audible {dba} dBA < 75 dBA", {"fire_alarm": a})
        if a.get("tested") is False:
            return GateResult(self.name, "HOLD", "Fire alarm not tested", {"fire_alarm": a})
        return GateResult(self.name, "PASS", "Fire alarm clear", {"fire_alarm": a})

class SmokeDamperAgent:
    name = "smoke-damper"
    def evaluate(self, ctx):
        d = ctx.get("smoke_damper") or {}
        if d.get("required") is False:
            return GateResult(self.name, "SKIP", "Smoke dampers N/A", {})
        close_s = _num(d.get("close_seconds"))
        if close_s is not None and close_s > 10:
            return GateResult(self.name, "FAIL", f"Damper close {close_s}s > 10s", {"smoke_damper": d})
        if d.get("actuation_pass") is False:
            return GateResult(self.name, "FAIL", "Smoke damper actuation failed", {"smoke_damper": d})
        if d.get("tested") is False:
            return GateResult(self.name, "HOLD", "Smoke dampers not tested", {"smoke_damper": d})
        return GateResult(self.name, "PASS", "Smoke dampers clear", {"smoke_damper": d})

class PunchTrackerAgent:
    name = "punch-tracker"
    def evaluate(self, ctx):
        p = ctx.get("punch") or {}
        reopen = _num(p.get("reopen_pct"))
        if reopen is not None and reopen >= 10:
            return GateResult(self.name, "HOLD", f"Punch reopen {reopen}% ≥ 10% — full floor redo", {"punch": p})
        if p.get("open_critical"):
            return GateResult(self.name, "HOLD", "Open critical punch items", {"punch": p})
        if p.get("walk_complete") is False:
            return GateResult(self.name, "HOLD", "Punch walk not complete", {"punch": p})
        return GateResult(self.name, "PASS", "Punch tracker clear", {"punch": p})

class TcoReadinessAgent:
    name = "tco-readiness"
    def evaluate(self, ctx):
        t = ctx.get("tco") or {}
        if t.get("binder_ready") is False:
            return GateResult(self.name, "HOLD", "TCO binder not ready for AHJ", {"tco": t})
        if t.get("ls_signoffs") is False:
            return GateResult(self.name, "HOLD", "Life-safety signoffs missing", {"tco": t})
        if (ctx.get("egress_lighting") or {}).get("emergency_power_fail"):
            return GateResult(self.name, "FAIL", "Cannot claim TCO — egress lighting emergency-power fail", {"tco": t})
        if (ctx.get("egress") or {}).get("blocked"):
            return GateResult(self.name, "FAIL", "Cannot claim TCO — egress blocked", {"tco": t})
        return GateResult(self.name, "PASS", "TCO readiness clear", {"tco": t})

class SafetyFailsafeAgent:
    name = "safety-failsafe"
    def evaluate(self, ctx):
        s = ctx.get("safety") or {}; violations = list(s.get("violations") or [])
        e = ctx.get("egress") or {}
        if e.get("blocked") or e.get("discharge_blocked"):
            violations.append("blocked egress / exit discharge")
        f = ctx.get("fire_door") or {}
        if f.get("label_missing") or f.get("seals_missing") or (f.get("failed") and not f.get("zone_reinspect")):
            violations.append("failed/unsafe fire door")
        gap_side = _num(f.get("gap_side_in")); gap_bottom = _num(f.get("gap_bottom_in"))
        if gap_side is not None and gap_side > 0.125:
            violations.append("fire door gap out of tolerance")
        if gap_bottom is not None and gap_bottom > 0.75:
            violations.append("fire door bottom gap out of tolerance")
        sp = ctx.get("sprinkler") or {}
        if sp.get("hydro_pass") is False or sp.get("uncapped_dry"):
            violations.append("sprinkler hydro/uncapped fail")
        fa = ctx.get("fire_alarm") or {}
        dba = _num(fa.get("audible_dba"))
        if fa.get("function_pass") is False or (dba is not None and dba < 75):
            violations.append("fire alarm function/dBA fail")
        if (ctx.get("egress_lighting") or {}).get("emergency_power_fail"):
            violations.append("egress lighting emergency-power fail")
        sd = ctx.get("smoke_damper") or {}
        close_s = _num(sd.get("close_seconds"))
        if sd.get("actuation_pass") is False or (close_s is not None and close_s > 10):
            violations.append("smoke damper close-time fail")
        if violations:
            return GateResult(self.name, "FAIL", "STOP-WORK: " + "; ".join(dict.fromkeys(violations)), {"violations": list(dict.fromkeys(violations))})
        return GateResult(self.name, "PASS", "No fail-safe violations", {})

class CrewOpsAgent:
    name = "crew-ops"
    def evaluate(self, ctx, require_briefing=True):
        crew = ctx.get("crew") or {}; roles = set(crew.get("roles") or [])
        missing = [r for r in ERECT_ROLES if r not in roles]
        if missing:
            return GateResult(self.name, "HOLD", "Missing roles: " + ", ".join(missing), {"missing": missing})
        if require_briefing and not crew.get("briefing_complete"):
            return GateResult(self.name, "HOLD", "LS briefing incomplete", {})
        return GateResult(self.name, "PASS", f"LS crew ready headcount={crew.get('headcount', len(roles))}", {})

class QaInspectorAgent:
    name = "qa-inspector"
    def evaluate(self, ctx, phase="pre"):
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-LS docs clear", {})
        if phase == "tco" and q.get("tco_binder_clear"):
            return GateResult(self.name, "PASS", "TCO binder docs clear", {})
        if phase not in ("pre",) and q.get("logs_clear"):
            return GateResult(self.name, "PASS", f"{phase} LS docs clear", {})
        return GateResult(self.name, "HOLD", f"No LS QA evidence for phase={phase}", {"qa": q})

class LsLeadAgent:
    name = "ls-lead"
    def assemble(self, ctx, gates, workflow):
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked life-safety sequence"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Life-safety sequence ready for {ctx.get('zone_id', 'zone')}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
