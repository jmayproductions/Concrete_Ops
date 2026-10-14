"""Deterministic specialist gates for Commissioning."""
from __future__ import annotations
from typing import Any
from modules.commissioning_swarm.schemas import GateResult

ERECT_ROLES = ('cx_lead', 'cxa', 'tab_tech', 'controls_tech', 'trade_foreman', 'owner_witness', 'safety_watch')

def _num(v, default=None):
    if v is None: return default
    try: return float(v)
    except (TypeError, ValueError): return default

class CxPlanAgent:
    name = "cx-plan"
    def evaluate(self, ctx):
        p = ctx.get("plan") or {}
        if not p.get("systems"):
            return GateResult(self.name, "HOLD", "Cx system list empty", {"plan": p})
        if p.get("approved") is False:
            return GateResult(self.name, "HOLD", "Cx plan not approved", {"plan": p})
        if not p.get("targets_defined"):
            return GateResult(self.name, "HOLD", "Performance targets not defined", {"plan": p})
        return GateResult(self.name, "PASS", "Cx plan clear", {"plan": p})

class PrefunctionalAgent:
    name = "prefunctional"
    def evaluate(self, ctx):
        p = ctx.get("prefunctional") or {}
        if p.get("install_complete") is False:
            return GateResult(self.name, "HOLD", "Install not complete for PF", {"prefunctional": p})
        if p.get("checklist_signed") is False:
            return GateResult(self.name, "HOLD", "Prefunctional checklist not signed", {"prefunctional": p})
        if p.get("open_critical_pf"):
            return GateResult(self.name, "HOLD", "Open critical prefunctional issues", {"prefunctional": p})
        return GateResult(self.name, "PASS", "Prefunctional clear", {"prefunctional": p})

class StartupSafeAgent:
    name = "startup-safe"
    def evaluate(self, ctx):
        s = ctx.get("startup") or {}
        if s.get("unsafe_energize"):
            return GateResult(self.name, "FAIL", "Unsafe energization/startup", {"startup": s})
        if s.get("loto_cleared") is False:
            return GateResult(self.name, "HOLD", "LOTO not cleared for startup", {"startup": s})
        if s.get("safeties_ok") is False:
            return GateResult(self.name, "HOLD", "Guards/safeties not verified", {"startup": s})
        return GateResult(self.name, "PASS", "Startup readiness clear", {"startup": s})

class TabBalanceAgent:
    name = "tab-balance"
    def evaluate(self, ctx):
        t = ctx.get("tab") or {}
        if t.get("required") is False:
            return GateResult(self.name, "SKIP", "TAB not required for this system", {})
        if t.get("within_tolerance") is False:
            return GateResult(self.name, "HOLD", "TAB out of tolerance", {"tab": t})
        if not t.get("report_attached"):
            return GateResult(self.name, "HOLD", "TAB report missing", {"tab": t})
        return GateResult(self.name, "PASS", "TAB clear", {"tab": t})

class FunctionalTestAgent:
    name = "functional-test"
    def evaluate(self, ctx):
        f = ctx.get("functional") or {}
        if f.get("script_complete") is False:
            return GateResult(self.name, "HOLD", "Functional test script incomplete", {"functional": f})
        if f.get("modes_proven") is False:
            return GateResult(self.name, "HOLD", "Required operating modes not proven", {"functional": f})
        if f.get("claimed_pass") and f.get("witness_required") and not f.get("witnessed"):
            return GateResult(self.name, "FAIL", "Functional pass claimed without witness", {"functional": f})
        return GateResult(self.name, "PASS", "Functional tests clear", {"functional": f})

class WitnessSignoffAgent:
    name = "witness-signoff"
    def evaluate(self, ctx):
        w = ctx.get("witness") or {}; f = ctx.get("functional") or {}
        required = w.get("required", f.get("witness_required", True))
        if required is False:
            return GateResult(self.name, "SKIP", "Witness not required", {})
        if not w.get("signed") and not f.get("witnessed"):
            return GateResult(self.name, "FAIL", "No witness sign-off — result invalid", {"witness": w})
        return GateResult(self.name, "PASS", "Witness sign-off clear", {"witness": w})

class CalibrationAgent:
    name = "calibration"
    def evaluate(self, ctx):
        c = ctx.get("calibration") or {}
        if c.get("required") is False:
            return GateResult(self.name, "SKIP", "Calibration N/A", {})
        if c.get("current") is False:
            return GateResult(self.name, "HOLD", "Critical sensors not calibrated", {"calibration": c})
        return GateResult(self.name, "PASS", "Calibration clear", {"calibration": c})

class PerformanceTolAgent:
    name = "performance-tol"
    def evaluate(self, ctx):
        p = ctx.get("performance") or {}
        dev = _num(p.get("deviation_pct"))
        limit = _num(p.get("limit_pct"), 10.0) or 10.0
        if dev is None and p.get("measured") is False:
            return GateResult(self.name, "HOLD", "Performance not measured", {"performance": p})
        if dev is not None and abs(dev) > limit and not p.get("retest_locked"):
            return GateResult(self.name, "FAIL", f"Performance deviation {dev}% > {limit}% — retest lock", {"performance": p})
        if p.get("retest_locked") and not p.get("retest_passed"):
            return GateResult(self.name, "HOLD", "Retest lock active — awaiting passing retest", {"performance": p})
        return GateResult(self.name, "PASS", "Performance within tolerance", {"performance": p})

class IssuesPunchAgent:
    name = "issues-punch"
    def evaluate(self, ctx):
        i = ctx.get("issues") or {}
        if i.get("open_critical"):
            return GateResult(self.name, "HOLD", "Open critical Cx issues", {"issues": i})
        if i.get("deferred_unsigned"):
            return GateResult(self.name, "HOLD", "Deferred Cx items not owner-accepted", {"issues": i})
        return GateResult(self.name, "PASS", "Cx issues clear", {"issues": i})

class OmTrainingAgent:
    name = "om-training"
    def evaluate(self, ctx):
        o = ctx.get("om") or {}
        if o.get("manuals_uploaded") is False:
            return GateResult(self.name, "HOLD", "O&M manuals not uploaded", {"om": o})
        if o.get("training_done") is False and o.get("training_scheduled") is False:
            return GateResult(self.name, "HOLD", "Operator training not done/scheduled", {"om": o})
        return GateResult(self.name, "PASS", "O&M/training clear", {"om": o})

class SeasonalDeferredAgent:
    name = "seasonal-deferred"
    def evaluate(self, ctx):
        s = ctx.get("seasonal") or {}
        if s.get("required") and not s.get("scheduled"):
            return GateResult(self.name, "HOLD", "Seasonal Cx required but unscheduled", {"seasonal": s})
        return GateResult(self.name, "PASS", "Seasonal/deferred Cx tracked", {"seasonal": s})

class LifeSafetyCxAgent:
    name = "life-safety-cx"
    def evaluate(self, ctx):
        l = ctx.get("life_safety") or {}
        if l.get("required") is False:
            return GateResult(self.name, "SKIP", "Life-safety Cx not in this run", {})
        if l.get("interface_failed"):
            return GateResult(self.name, "FAIL", "Life-safety interface test failed", {"life_safety": l})
        if l.get("tested") is False:
            return GateResult(self.name, "HOLD", "Life-safety Cx interfaces not tested", {"life_safety": l})
        return GateResult(self.name, "PASS", "Life-safety Cx clear", {"life_safety": l})

class SafetyFailsafeAgent:
    name = "safety-failsafe"
    def evaluate(self, ctx):
        s = ctx.get("safety") or {}; violations = list(s.get("violations") or [])
        f = ctx.get("functional") or {}; w = ctx.get("witness") or {}
        if f.get("claimed_pass") and (f.get("witness_required") or w.get("required", True)) and not (f.get("witnessed") or w.get("signed")):
            violations.append("pass without witness sign-off")
        p = ctx.get("performance") or {}
        dev = _num(p.get("deviation_pct")); limit = _num(p.get("limit_pct"), 10.0) or 10.0
        if dev is not None and abs(dev) > limit and not p.get("retest_passed"):
            violations.append("performance deviation >10% without passing retest")
        if (ctx.get("startup") or {}).get("unsafe_energize"):
            violations.append("unsafe energization/startup")
        if (ctx.get("life_safety") or {}).get("interface_failed"):
            violations.append("life-safety interface failed")
        if (ctx.get("issues") or {}).get("open_critical") and (ctx.get("issues") or {}).get("handover_forced"):
            violations.append("critical Cx issues at forced handover")
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
            return GateResult(self.name, "HOLD", "Cx briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Cx crew ready headcount={crew.get('headcount', len(roles))}", {})

class QaInspectorAgent:
    name = "qa-inspector"
    def evaluate(self, ctx, phase="pre"):
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-Cx docs clear", {})
        if phase == "closeout" and q.get("cx_binder_clear"):
            return GateResult(self.name, "PASS", "Cx binder/closeout clear", {})
        if phase not in ("pre",) and q.get("logs_clear"):
            return GateResult(self.name, "PASS", f"{phase} Cx docs clear", {})
        return GateResult(self.name, "HOLD", f"No Cx QA evidence for phase={phase}", {"qa": q})

class CxLeadAgent:
    name = "cx-lead"
    def assemble(self, ctx, gates, workflow):
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked commissioning sequence"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Commissioning sequence ready for {ctx.get('zone_id', ctx.get('system_id', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
