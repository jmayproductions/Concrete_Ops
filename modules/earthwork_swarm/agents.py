"""Deterministic specialist gates for earthwork / site civil."""

from __future__ import annotations

from typing import Any

from modules.earthwork_swarm.schemas import GateResult

ERECT_ROLES = ('earthwork_lead', 'excavator_op', 'grader_op', 'roller_op', 'laborer', 'qc_tech', 'safety_watch')
DEFAULT_MAX_LIFT_IN = 12.0


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class MaterialsFillAgent:
    name = "materials-fill"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("materials") or {}
        if m.get("required") is False:
            return GateResult(self.name, "PASS", "No import fill this gate", {"materials": m})
        miss = _missing(m, ("import_approved", "organics_ok", "aggregate_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Fill materials incomplete: " + ", ".join(miss), {"materials": m})
        if m.get("contaminated") or m.get("frozen_load"):
            return GateResult(self.name, "HOLD", "Contaminated or frozen fill rejected", {"materials": m})
        return GateResult(self.name, "PASS", "Fill/aggregate materials clear", {"materials": m})


class SurveyControlAgent:
    name = "survey-control"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("survey") or {}
        miss = _missing(s, ("benchmarks_ok", "stakes_current"))
        if miss:
            return GateResult(self.name, "HOLD", "Survey control incomplete: " + ", ".join(miss), {"survey": s})
        if s.get("grade_out_of_tolerance"):
            return GateResult(self.name, "HOLD", "Grade out of tolerance — re-stake/rework", {"survey": s})
        return GateResult(self.name, "PASS", "Survey/control clear", {"survey": s})


class UtilitiesLocateAgent:
    name = "utilities-locate"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        u = ctx.get("utilities") or {}
        if u.get("dig_without_locate") or u.get("utility_strike"):
            return GateResult(self.name, "FAIL", "STOP-WORK: dig without locate or utility strike", {"utilities": u})
        miss = _missing(u, ("ticket_valid", "marks_visible"))
        if miss:
            return GateResult(self.name, "HOLD", "Utility locate incomplete: " + ", ".join(miss), {"utilities": u})
        if u.get("conflict_unresolved"):
            return GateResult(self.name, "HOLD", "Utility conflict unresolved — soft dig / redesign", {"utilities": u})
        return GateResult(self.name, "PASS", "Utility locate clear", {"utilities": u})


class ExcavationAgent:
    name = "excavation"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("excavation") or {}
        if e.get("overcut_unapproved"):
            return GateResult(self.name, "HOLD", "Over-excavation without engineer direction", {"excavation": e})
        if e.get("spoil_at_crest"):
            return GateResult(self.name, "HOLD", "Spoil surcharge at crest — pull back", {"excavation": e})
        if e.get("unprotected_deep"):
            return GateResult(self.name, "FAIL", "Unprotected deep excavation / trench", {"excavation": e})
        if e.get("to_plan") is False:
            return GateResult(self.name, "HOLD", "Excavation not to plan lines/grades", {"excavation": e})
        return GateResult(self.name, "PASS", "Excavation geometry clear", {"excavation": e})


class SubgradeAgent:
    name = "subgrade"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("subgrade") or {}
        if not s.get("proof_roll_done"):
            return GateResult(self.name, "HOLD", "Proof-roll not completed", {"subgrade": s})
        if s.get("pumping") or s.get("soft_spots_open"):
            return GateResult(self.name, "HOLD", "Pumping/soft spots not undercut/replaced", {"subgrade": s})
        if s.get("accepted") is False:
            return GateResult(self.name, "HOLD", "Subgrade not accepted", {"subgrade": s})
        return GateResult(self.name, "PASS", "Subgrade acceptance clear", {"subgrade": s})


class CompactionAgent:
    name = "compaction"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("compaction") or {}
        if c.get("required") is False:
            return GateResult(self.name, "PASS", "No compaction this gate", {"compaction": c})
        lift = _num(c.get("lift_in"))
        max_lift = _num(c.get("max_lift_in"), DEFAULT_MAX_LIFT_IN) or DEFAULT_MAX_LIFT_IN
        if lift is not None and lift > max_lift:
            return GateResult(self.name, "HOLD", f"Lift {lift}in > {max_lift}in max", {"compaction": c})
        if c.get("density_ok") is False:
            return GateResult(self.name, "HOLD", "Density test failed — rework lift", {"compaction": c})
        if c.get("moisture_ok") is False:
            return GateResult(self.name, "HOLD", "Moisture out of window", {"compaction": c})
        if not c.get("tests_logged"):
            return GateResult(self.name, "HOLD", "Density tests not logged for lift/area", {"compaction": c})
        return GateResult(self.name, "PASS", "Compaction lifts clear", {"compaction": c})


class TrenchBackfillAgent:
    name = "trench-backfill"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("trench") or {}
        if not t and not ctx.get("require_trench"):
            return GateResult(self.name, "SKIP", "No trench scope", {})
        miss = _missing(t, ("bedding_ok", "haunching_ok", "compacted"))
        if miss:
            return GateResult(self.name, "HOLD", "Trench backfill incomplete: " + ", ".join(miss), {"trench": t})
        if t.get("rocks_on_pipe"):
            return GateResult(self.name, "HOLD", "Oversized rock on pipe — rework shading", {"trench": t})
        return GateResult(self.name, "PASS", "Trench backfill clear", {"trench": t})


class DrainageSwalesAgent:
    name = "drainage-swales"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("drainage") or {}
        if d.get("ponding"):
            return GateResult(self.name, "HOLD", "Ponding against work / foundations", {"drainage": d})
        if d.get("grade_reversed"):
            return GateResult(self.name, "HOLD", "Swale/ditch grade reversed", {"drainage": d})
        if not d.get("temp_drainage_ok") and not d.get("permanent_ok"):
            return GateResult(self.name, "HOLD", "No temporary or permanent drainage confirmed", {"drainage": d})
        return GateResult(self.name, "PASS", "Drainage/swales clear", {"drainage": d})


class ErosionControlAgent:
    name = "erosion-control"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("erosion") or {}
        if not e.get("perimeter_bmps"):
            return GateResult(self.name, "HOLD", "Perimeter BMPs missing before disturb", {"erosion": e})
        if e.get("inlet_protection") is False:
            return GateResult(self.name, "HOLD", "Inlet protection missing/deficient", {"erosion": e})
        if e.get("entrance_stabilized") is False:
            return GateResult(self.name, "HOLD", "Construction entrance not stabilized", {"erosion": e})
        return GateResult(self.name, "PASS", "Erosion control clear", {"erosion": e})


class PavingPrepAgent:
    name = "paving-prep"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("paving") or {}
        if not p and not ctx.get("require_paving"):
            return GateResult(self.name, "SKIP", "No paving prep scope", {})
        miss = _missing(p, ("final_grade_ok", "base_thickness_ok", "base_compacted"))
        if miss:
            return GateResult(self.name, "HOLD", "Paving prep incomplete: " + ", ".join(miss), {"paving": p})
        if p.get("soft_spots"):
            return GateResult(self.name, "HOLD", "Soft spots remain in pave section", {"paving": p})
        return GateResult(self.name, "PASS", "Paving prep clear", {"paving": p})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        holds = []
        if w.get("frozen_subgrade") and not w.get("freeze_procedures"):
            holds.append("frozen subgrade/fill without procedures")
        if w.get("saturated") and not w.get("dry_workable"):
            holds.append("saturated/pumping soils for structural fill")
        if w.get("active_storm") and not w.get("slopes_protected"):
            holds.append("storm with unprotected open excavations/slopes")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/protection CLEAR", {"weather": w})


class GeotechAgent:
    name = "geotech"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("geotech") or {}
        if g.get("required") is False:
            return GateResult(self.name, "PASS", "Geotech hold not required this gate", {"geotech": g})
        if not g.get("recommendations_followed"):
            return GateResult(self.name, "HOLD", "Geotech recommendations not followed", {"geotech": g})
        if g.get("si_density_required") and not g.get("si_density_complete"):
            return GateResult(self.name, "HOLD", "Special inspection density tests incomplete", {"geotech": g})
        if not g.get("accepted"):
            return GateResult(self.name, "HOLD", "Geotech acceptance missing", {"geotech": g})
        return GateResult(self.name, "PASS", "Geotech hold points clear", {"geotech": g})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        u = ctx.get("utilities") or {}
        e = ctx.get("excavation") or {}
        if u.get("dig_without_locate") or u.get("utility_strike"):
            violations.append("utility locate strike / dig without ticket")
        if e.get("unprotected_deep"):
            violations.append("unprotected deep excavation")
        if e.get("spoil_at_crest") and e.get("collapse_risk"):
            violations.append("spoil surcharge collapse risk")
        if ctx.get("slope", {}).get("unstable"):
            violations.append("unstable slope / cave-in indicators")
        if s.get("no_competent_person") and (e.get("depth_ft") or 0) >= 5:
            violations.append("no excavation competent person")
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
            return GateResult(self.name, "PASS", "Pre-earthwork QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class EarthworkLeadAgent:
    name = "earthwork-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked earthwork"
        elif any(g.agent == "utilities-locate" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Utility locate fail-safe blocked dig"
        elif any(g.agent == "excavation" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Excavation safety blocked dig"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
