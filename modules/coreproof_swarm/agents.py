"""Deterministic specialist gates for CoreProof lab verification."""
from __future__ import annotations
from typing import Any
from modules.coreproof_swarm.schemas import GateResult

ERECT_ROLES = ('lab_lead', 'field_tech', 'lab_tech', 'break_tech', 'qc_tech', 'engineer_reviewer', 'safety_watch')

def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

class SampleIdAgent:
    name = "sample-id"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("sample") or {}
        if not s.get("sample_id"):
            return GateResult(self.name, "HOLD", "Sample ID missing", {"sample": s})
        if not s.get("pour_zone") or not s.get("cast_time_known"):
            return GateResult(self.name, "HOLD", "Pour zone/cast time not labeled", {"sample": s})
        if s.get("traceable") is False:
            return GateResult(self.name, "HOLD", "Sample not traceable to mix/ticket", {"sample": s})
        return GateResult(self.name, "PASS", f"Sample ID clear ({s.get('sample_id')})", {"sample": s})

class CastHandlingAgent:
    name = "cast-handling"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("cast") or {}
        if c.get("cracked_green") or c.get("mold_damaged"):
            return GateResult(self.name, "FAIL", "Green cylinder cracked / mold damaged", {"cast": c})
        if c.get("method_ok") is False:
            return GateResult(self.name, "HOLD", "Cast method not per ASTM/procedure", {"cast": c})
        return GateResult(self.name, "PASS", "Cast handling clear", {"cast": c})

class InitialCureAgent:
    name = "initial-cure"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        i = ctx.get("initial_cure") or {}
        tmin = _num(i.get("temp_min_c")); tmax = _num(i.get("temp_max_c"))
        if i.get("frozen"):
            return GateResult(self.name, "FAIL", "Initial cure freeze damage", {"initial_cure": i})
        if tmin is not None and tmin < 16:
            return GateResult(self.name, "HOLD", f"Initial cure low temp {tmin}C < 16C", {"initial_cure": i})
        if tmax is not None and tmax > 27:
            return GateResult(self.name, "HOLD", f"Initial cure high temp {tmax}C > 27C", {"initial_cure": i})
        if not i.get("logged"):
            return GateResult(self.name, "HOLD", "Initial cure temp not logged", {"initial_cure": i})
        return GateResult(self.name, "PASS", "Initial cure clear", {"initial_cure": i})

class TransportLabAgent:
    name = "transport-lab"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("transport") or {}
        if t.get("shock_damage") or t.get("unprotected"):
            return GateResult(self.name, "HOLD", "Transport mishandling / unprotected", {"transport": t})
        if t.get("rigid_box") is False:
            return GateResult(self.name, "HOLD", "No rigid/shock-protected transport box", {"transport": t})
        return GateResult(self.name, "PASS", "Transport to lab clear", {"transport": t})

class MoistLabCureAgent:
    name = "moist-lab-cure"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("lab_cure") or {}
        if m.get("moist") is False:
            return GateResult(self.name, "HOLD", "Lab moist cure not maintained", {"lab_cure": m})
        if m.get("continuous") is False:
            return GateResult(self.name, "HOLD", "Lab cure interrupted", {"lab_cure": m})
        return GateResult(self.name, "PASS", "Moist lab cure clear", {"lab_cure": m})

class BreakScheduleAgent:
    name = "break-schedule"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("break") or {}
        if b.get("within_tolerance") is False:
            return GateResult(self.name, "HOLD", "Break outside ±2 hr age window", {"break": b})
        if not b.get("age_days"):
            return GateResult(self.name, "HOLD", "Break age not recorded", {"break": b})
        return GateResult(self.name, "PASS", f"Break schedule clear ({b.get('age_days')}d)", {"break": b})

class CylinderAstm39Agent:
    name = "cylinder-astm39"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("cylinder") or {}
        if c.get("required") is False:
            return GateResult(self.name, "SKIP", "Cylinder break not in this run", {})
        if c.get("ends_prepped") is False:
            return GateResult(self.name, "HOLD", "Cylinder ends not capped/ground", {"cylinder": c})
        if _num(c.get("strength_mpa")) is None and _num(c.get("avg_mpa")) is None:
            return GateResult(self.name, "HOLD", "Cylinder strength not recorded", {"cylinder": c})
        if c.get("set_complete") is False:
            return GateResult(self.name, "HOLD", "Cylinder set incomplete", {"cylinder": c})
        return GateResult(self.name, "PASS", "ASTM C39 cylinder clear", {"cylinder": c})

class CoreAstm42Agent:
    name = "core-astm42"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("core") or {}
        if c.get("required") is False and not c.get("tested"):
            return GateResult(self.name, "SKIP", "Core test not required", {})
        ld = _num(c.get("ld_ratio"), 2.0) or 2.0
        factor = 0.95 if ld < 2.0 else 1.0
        if c.get("adjustment_factor") is not None:
            factor = _num(c.get("adjustment_factor"), factor) or factor
        strength = _num(c.get("strength_mpa"))
        adjusted = None if strength is None else strength * factor
        fc = _num(c.get("fc_mpa") or (ctx.get("spec") or {}).get("fc_mpa"))
        if c.get("moist_post_drill_48h") is False:
            return GateResult(self.name, "HOLD", "Core missing 48h moist cure post-drill", {"core": c})
        if c.get("ends_prepped") is False:
            return GateResult(self.name, "HOLD", "Core ends not prepared", {"core": c})
        if adjusted is not None and fc is not None and adjusted < 0.85 * fc:
            return GateResult(self.name, "FAIL", f"Core {adjusted:.1f} MPa < 85% of f'c {fc} (adj)", {"core": c, "adjusted_mpa": adjusted, "factor": factor})
        return GateResult(self.name, "PASS", "ASTM C42 core clear", {"core": c, "adjusted_mpa": adjusted, "factor": factor})

class FlexuralBeamAgent:
    name = "flexural-beam"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("flexural") or {}
        if f.get("required") is False:
            return GateResult(self.name, "SKIP", "Flexural not required", {})
        if f.get("meets_spec") is False:
            return GateResult(self.name, "HOLD", "Flexural MOR below spec", {"flexural": f})
        return GateResult(self.name, "PASS", "Flexural beam clear", {"flexural": f})

class StrengthComplianceAgent:
    name = "strength-compliance"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("strength") or {}
        spec = ctx.get("spec") or {}
        fc = _num(s.get("fc_mpa") or spec.get("fc_mpa"))
        avg = _num(s.get("avg_mpa") or (ctx.get("cylinder") or {}).get("avg_mpa"))
        lowest = _num(s.get("lowest_mpa") or (ctx.get("cylinder") or {}).get("lowest_mpa"))
        consec = int(s.get("consecutive_below") or 0)
        if fc is None or avg is None:
            return GateResult(self.name, "HOLD", "f'c or average strength missing", {"strength": s, "spec": spec})
        if avg < fc - 3.5:
            return GateResult(self.name, "FAIL", f"Avg {avg} MPa < f'c {fc} by >3.5 MPa — engineer review", {"strength": s})
        if consec >= 2:
            return GateResult(self.name, "FAIL", "Two consecutive tests < f'c — trigger cores / investigation", {"strength": s})
        if lowest is not None and lowest < fc and avg >= fc:
            return GateResult(self.name, "PASS", "ACI pass — one low, avg ≥ f'c", {"strength": s})
        if avg >= fc and (lowest is None or lowest >= fc):
            return GateResult(self.name, "PASS", "Strength compliance PASS", {"strength": s})
        if avg < fc:
            return GateResult(self.name, "HOLD", f"Avg {avg} MPa below f'c {fc} — review", {"strength": s})
        return GateResult(self.name, "PASS", "Strength compliance clear", {"strength": s})

class FieldVsLabAgent:
    name = "field-vs-lab"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("field_lab") or {}
        if f.get("required") is False:
            return GateResult(self.name, "SKIP", "Field vs lab comparison not requested", {})
        ratio = _num(f.get("field_to_lab_ratio"))
        if ratio is not None and ratio < 0.70:
            return GateResult(self.name, "HOLD", f"Field/lab ratio {ratio:.2f} < 0.70 — QA review", {"field_lab": f})
        if f.get("lab_suspiciously_high"):
            return GateResult(self.name, "HOLD", "Lab results >105% spec — check lab cure temps", {"field_lab": f})
        return GateResult(self.name, "PASS", "Field vs lab deviation acceptable", {"field_lab": f})

class HandlingDeviationAgent:
    name = "handling-deviation"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        h = ctx.get("handling") or {}
        score = _num(h.get("deviation_score"), 0) or 0
        if h.get("invalid_as_sole_evidence"):
            return GateResult(self.name, "FAIL", "Mishandled samples used as sole acceptance evidence", {"handling": h})
        if score >= 8:
            return GateResult(self.name, "HOLD", f"High handling deviation score {score}", {"handling": h})
        return GateResult(self.name, "PASS", "Handling deviation acceptable", {"handling": h})

class SafetyFailsafeAgent:
    name = "safety-failsafe"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}; violations = list(s.get("violations") or [])
        strength = ctx.get("strength") or {}; spec = ctx.get("spec") or {}
        fc = _num(strength.get("fc_mpa") or spec.get("fc_mpa"))
        avg = _num(strength.get("avg_mpa") or (ctx.get("cylinder") or {}).get("avg_mpa"))
        if fc is not None and avg is not None and avg < fc - 3.5:
            violations.append("average strength more than 3.5 MPa below f'c")
        if int(strength.get("consecutive_below") or 0) >= 2:
            violations.append("two consecutive tests below f'c")
        core = ctx.get("core") or {}
        if core.get("required") or core.get("tested"):
            ld = _num(core.get("ld_ratio"), 2.0) or 2.0
            factor = _num(core.get("adjustment_factor"), 0.95 if ld < 2.0 else 1.0) or 1.0
            cstr = _num(core.get("strength_mpa"))
            cfc = _num(core.get("fc_mpa") or fc)
            if cstr is not None and cfc is not None and cstr * factor < 0.85 * cfc:
                violations.append("core below 85% f'c after adjustment")
        if (ctx.get("initial_cure") or {}).get("frozen"):
            violations.append("freeze-damaged initial cure")
        if (ctx.get("cast") or {}).get("cracked_green"):
            violations.append("cracked green cylinders")
        if (ctx.get("handling") or {}).get("invalid_as_sole_evidence"):
            violations.append("invalid mishandled samples as sole evidence")
        if violations:
            return GateResult(self.name, "FAIL", "STOP-WORK: " + "; ".join(dict.fromkeys(violations)), {"violations": list(dict.fromkeys(violations))})
        return GateResult(self.name, "PASS", "No fail-safe violations", {})

class CrewOpsAgent:
    name = "crew-ops"
    def evaluate(self, ctx: dict[str, Any], require_briefing: bool = True) -> GateResult:
        crew = ctx.get("crew") or {}; roles = set(crew.get("roles") or [])
        missing = [r for r in ERECT_ROLES if r not in roles]
        if missing:
            return GateResult(self.name, "HOLD", "Missing roles: " + ", ".join(missing), {"missing": missing})
        if require_briefing and not crew.get("briefing_complete"):
            return GateResult(self.name, "HOLD", "Sampling/lab briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Lab crew ready headcount={crew.get('headcount', len(roles))}", {})

class QaInspectorAgent:
    name = "qa-inspector"
    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-sample docs clear", {})
        if phase == "report" and q.get("break_reports_clear"):
            return GateResult(self.name, "PASS", "Break reports clear", {})
        if phase not in ("pre",) and q.get("coc_clear"):
            return GateResult(self.name, "PASS", f"{phase} lab docs clear", {})
        return GateResult(self.name, "HOLD", f"No lab QA evidence for phase={phase}", {"qa": q})

class LabLeadAgent:
    name = "lab-lead"
    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked lab/strength sequence"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Lab sequence ready for {ctx.get('zone_id', ctx.get('sample', {}).get('sample_id', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
