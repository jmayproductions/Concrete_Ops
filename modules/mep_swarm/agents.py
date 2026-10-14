"""Deterministic specialist gates for MEP rough-in + firestop."""

from __future__ import annotations

from typing import Any

from modules.mep_swarm.schemas import GateResult

ERECT_ROLES = ('mep_lead', 'hvac_tech', 'electrician', 'plumber', 'firestop_tech', 'qc_tech', 'safety_watch')


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class ClashCoordAgent:
    name = "clash-coord"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("clash") or {}
        if c.get("resolved") is False or c.get("unresolved"):
            return GateResult(self.name, "HOLD", "Unresolved MEP clashes: " + ", ".join(c.get("unresolved") or ["see BIM"]), {"clash": c})
        if not c.get("sleeve_map_published"):
            return GateResult(self.name, "HOLD", "Sleeve/opening map not published", {"clash": c})
        return GateResult(self.name, "PASS", "Clash/coordination clear", {"clash": c})


class SleevePenetrationAgent:
    name = "sleeve-penetration"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("sleeves") or {}
        if not s.get("placed_per_map"):
            return GateResult(self.name, "HOLD", "Sleeves not placed per opening map", {"sleeves": s})
        if s.get("gross_offset"):
            return GateResult(self.name, "HOLD", "Sleeve offset beyond tolerance — halt and re-core/plan", {"sleeves": s})
        if s.get("missing_on_rated"):
            return GateResult(self.name, "HOLD", "Missing sleeves on rated assemblies: " + ", ".join(s["missing_on_rated"]), {"sleeves": s})
        return GateResult(self.name, "PASS", "Sleeves/penetrations clear", {"sleeves": s})


class HvacRoughAgent:
    name = "hvac-rough"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        h = ctx.get("hvac") or {}
        if not h and not ctx.get("require_hvac"):
            return GateResult(self.name, "SKIP", "No HVAC scope", {})
        miss = _missing(h, ("seams_sealed", "hangers_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "HVAC incomplete: " + ", ".join(miss), {"hvac": h})
        if h.get("dampers_incomplete"):
            return GateResult(self.name, "HOLD", "Fire/smoke dampers incomplete/inaccessible", {"hvac": h})
        return GateResult(self.name, "PASS", "HVAC rough clear", {"hvac": h})


class ElectricalRoughAgent:
    name = "electrical-rough"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("electrical") or {}
        if not e and not ctx.get("require_electrical"):
            return GateResult(self.name, "SKIP", "No electrical scope", {})
        miss = _missing(e, ("conduit_ok", "fill_ok", "panels_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Electrical incomplete: " + ", ".join(miss), {"electrical": e})
        if e.get("grounding_fail") or e.get("ir_fail"):
            return GateResult(self.name, "HOLD", "Grounding/IR test failed", {"electrical": e})
        return GateResult(self.name, "PASS", "Electrical rough clear", {"electrical": e})


class PlumbingRoughAgent:
    name = "plumbing-rough"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("plumbing") or {}
        if not p and not ctx.get("require_plumbing"):
            return GateResult(self.name, "SKIP", "No plumbing scope", {})
        if p.get("slope_ok") is False:
            return GateResult(self.name, "HOLD", "DWV slope insufficient/reversed", {"plumbing": p})
        miss = _missing(p, ("layout_ok",))
        if miss:
            return GateResult(self.name, "HOLD", "Plumbing incomplete: " + ", ".join(miss), {"plumbing": p})
        return GateResult(self.name, "PASS", "Plumbing rough clear", {"plumbing": p})


class FirestopAgent:
    name = "firestop"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("firestop") or {}
        if f.get("required") is False:
            return GateResult(self.name, "PASS", "No firestop scope this zone", {"firestop": f})
        if f.get("wrong_ul_system"):
            return GateResult(self.name, "FAIL", "UL system mismatch vs submittal", {"firestop": f})
        if f.get("covered_without_inspection"):
            return GateResult(self.name, "FAIL", "Rated penetration covered without firestop inspection", {"firestop": f})
        miss = _missing(f, ("ul_matched", "photos_before_cover", "log_signed"))
        if miss:
            return GateResult(self.name, "HOLD", "Firestop incomplete: " + ", ".join(miss), {"firestop": f})
        return GateResult(self.name, "PASS", "Firestop pre-cover clear", {"firestop": f})


class DamperLifeSafetyAgent:
    name = "damper-life-safety"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("dampers") or {}
        if not d and not ctx.get("require_dampers"):
            return GateResult(self.name, "SKIP", "No damper scope", {})
        miss = _missing(d, ("installed", "accessible", "tagged"))
        if miss:
            return GateResult(self.name, "HOLD", "Dampers incomplete: " + ", ".join(miss), {"dampers": d})
        if d.get("actuation_required") and not d.get("actuation_passed"):
            return GateResult(self.name, "HOLD", "Damper actuation/close test not passed", {"dampers": d})
        return GateResult(self.name, "PASS", "Damper/life-safety clear", {"dampers": d})


class ShaftAccessAgent:
    name = "shaft-access"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("shaft") or {}
        if not s and not ctx.get("require_shaft"):
            return GateResult(self.name, "SKIP", "No shaft scope", {})
        if s.get("missing_access_hatch"):
            return GateResult(self.name, "HOLD", "Missing required shaft access hatch", {"shaft": s})
        if s.get("clearance_conflict"):
            return GateResult(self.name, "HOLD", "Stack clearance conflict", {"shaft": s})
        if not s.get("trade_sequence_ok"):
            return GateResult(self.name, "HOLD", "Shaft trade sequence/access plan incomplete", {"shaft": s})
        return GateResult(self.name, "PASS", "Shaft access/routing clear", {"shaft": s})


class PressureTestAgent:
    name = "pressure-test"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("pressure_test") or {}
        if t.get("required") is False:
            return GateResult(self.name, "PASS", "Pressure/DALT not required this gate", {"pressure_test": t})
        if not t.get("performed"):
            return GateResult(self.name, "HOLD", "Required pressure/DALT/IR test not performed", {"pressure_test": t})
        if t.get("passed") is False:
            return GateResult(self.name, "FAIL", f"Test failed: {t.get('notes', 'see report')}", {"pressure_test": t})
        return GateResult(self.name, "PASS", "Pressure/leakage tests clear", {"pressure_test": t})


class InsulationHangersAgent:
    name = "insulation-hangers"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        i = ctx.get("insulation") or {}
        if not i:
            return GateResult(self.name, "SKIP", "No insulation/hanger gate", {})
        if i.get("hangers_ok") is False:
            return GateResult(self.name, "HOLD", "Hanger spacing/support deficient", {"insulation": i})
        if i.get("insulation_complete") is False:
            return GateResult(self.name, "HOLD", "Required insulation incomplete before cover", {"insulation": i})
        return GateResult(self.name, "PASS", "Insulation/hangers clear", {"insulation": i})


class LabelingAsbuiltAgent:
    name = "labeling-asbuilt"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("labeling") or {}
        if not l:
            return GateResult(self.name, "SKIP", "No labeling scope", {})
        if l.get("critical_unlabeled"):
            return GateResult(self.name, "HOLD", "Unlabeled devices: " + ", ".join(l["critical_unlabeled"]), {"labeling": l})
        if l.get("redlines_current") is False:
            return GateResult(self.name, "HOLD", "As-built redlines not current", {"labeling": l})
        return GateResult(self.name, "PASS", "Labeling/as-builts clear", {"labeling": l})


class WeatherGateAgent:
    name = "weather-gate"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            if ctx.get("exterior_scope"):
                return GateResult(self.name, "HOLD", "No weather data for exterior MEP", {})
            return GateResult(self.name, "PASS", "Interior scope — weather N/A", {})
        holds = []
        if w.get("lightning"):
            holds.append("lightning")
        wind = _num(w.get("wind_kph"), 0) or 0
        if wind >= (_num(w.get("wind_hold_kph"), 55) or 55):
            holds.append(f"wind {wind}kph")
        if w.get("freeze_risk") and w.get("water_test_exposed"):
            holds.append("freeze risk during water test")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather CLEAR", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("electrical", {}).get("energized_without_loto"):
            violations.append("energized work without LOTO")
        if ctx.get("firestop", {}).get("covered_without_inspection"):
            violations.append("covering rated penetration without firestop inspection")
        if ctx.get("shaft", {}).get("entry_without_controls"):
            violations.append("shaft entry without controls")
        if violations:
            return GateResult(self.name, "FAIL", "STOP-WORK: " + "; ".join(violations), {"violations": violations})
        return GateResult(self.name, "PASS", "No fail-safe violations", {})


class CrewOpsAgent:
    name = "crew-ops"

    def evaluate(self, ctx: dict[str, Any], require_briefing: bool = True) -> GateResult:
        crew = ctx.get("crew") or {}
        roles = set(crew.get("roles") or [])
        missing = [r for r in ERECT_ROLES if r not in roles]
        if missing:
            return GateResult(self.name, "HOLD", "Missing roles: " + ", ".join(missing), {"missing": missing})
        if crew.get("fatigued_workers"):
            return GateResult(self.name, "HOLD", "Fatigue risk: " + ", ".join(crew["fatigued_workers"]), {})
        if require_briefing and not crew.get("briefing_complete"):
            return GateResult(self.name, "HOLD", "Crew briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Crew ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-MEP QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class MepLeadAgent:
    name = "mep-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked MEP work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
