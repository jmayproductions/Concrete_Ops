"""Deterministic specialist gates for deep foundations."""

from __future__ import annotations

from typing import Any

from modules.deep_foundations_swarm.schemas import GateResult

ERECT_ROLES = ('foundations_lead', 'drill_op', 'crane_op', 'cage_crew', 'concrete_tech', 'qc_tech', 'safety_watch')


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class MaterialsConcreteAgent:
    name = "materials-concrete"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("materials") or {}
        miss = _missing(m, ("mix_approved", "cage_shops_approved", "certs_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Materials incomplete: " + ", ".join(miss), {"materials": m})
        return GateResult(self.name, "PASS", "Mix/cage/pile materials clear", {"materials": m})


class SurveyLayoutAgent:
    name = "survey-layout"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("survey") or {}
        if not s.get("staked"):
            return GateResult(self.name, "HOLD", "Pile/shaft centers not staked", {"survey": s})
        if s.get("location_out_of_tolerance"):
            return GateResult(self.name, "HOLD", "As-built location out of tolerance", {"survey": s})
        return GateResult(self.name, "PASS", "Layout/stake clear", {"survey": s})


class DrillingAugerAgent:
    name = "drilling-auger"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("drilling") or {}
        if d.get("required") is False:
            return GateResult(self.name, "SKIP", "No drilled shaft this gate", {})
        if d.get("collapse"):
            return GateResult(self.name, "HOLD", "Hole collapse / cave-in — stabilize", {"drilling": d})
        if d.get("diameter_ok") is False or d.get("depth_ok") is False:
            return GateResult(self.name, "HOLD", "Diameter/depth not to plan", {"drilling": d})
        if d.get("verticality_ok") is False:
            return GateResult(self.name, "HOLD", "Verticality out of tolerance", {"drilling": d})
        return GateResult(self.name, "PASS", "Drilled shaft excavation clear", {"drilling": d})


class CasingSlurryAgent:
    name = "casing-slurry"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("casing_slurry") or {}
        if c.get("required") is False:
            return GateResult(self.name, "PASS", "Dry hole — casing/slurry not required", {"casing_slurry": c})
        if c.get("unstable"):
            return GateResult(self.name, "HOLD", "Hole unstable — advance casing / restore slurry head", {"casing_slurry": c})
        if c.get("slurry_in_spec") is False:
            return GateResult(self.name, "HOLD", "Slurry properties out of spec", {"casing_slurry": c})
        return GateResult(self.name, "PASS", "Casing/slurry stability clear", {"casing_slurry": c})


class TipElevationAgent:
    name = "tip-elevation"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("tip") or {}
        if not t.get("at_criteria"):
            return GateResult(self.name, "HOLD", "Tip not at design elevation/refusal criteria", {"tip": t})
        sediment = _num(t.get("sediment_in"), 0.0) or 0.0
        max_sed = _num(t.get("max_sediment_in"), 1.0) or 1.0
        if sediment > max_sed:
            return GateResult(self.name, "HOLD", f"Sediment {sediment}in > {max_sed}in max — re-clean", {"tip": t})
        if t.get("cleanout_done") is False:
            return GateResult(self.name, "HOLD", "Cleanout not complete", {"tip": t})
        return GateResult(self.name, "PASS", "Tip elevation/cleanout clear", {"tip": t})


class CageRebarAgent:
    name = "cage-rebar"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("cage") or {}
        miss = _missing(c, ("matches_shops", "spacers_ok", "elevation_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Cage incomplete: " + ", ".join(miss), {"cage": c})
        if c.get("contaminated"):
            return GateResult(self.name, "HOLD", "Cage contaminated — clean/replace before concrete", {"cage": c})
        return GateResult(self.name, "PASS", "Cage placement clear", {"cage": c})


class ConcretePlacementAgent:
    name = "concrete-placement"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("concrete") or {}
        if p.get("required") is False:
            return GateResult(self.name, "SKIP", "No concrete placement this gate", {})
        if p.get("wet_hole") and not p.get("tremie"):
            return GateResult(self.name, "HOLD", "Wet hole requires tremie placement", {"concrete": p})
        if p.get("pour_interrupted"):
            return GateResult(self.name, "HOLD", "Tremie/pour interrupted — cold joint risk", {"concrete": p})
        actual = _num(p.get("volume_cy"))
        theoretical = _num(p.get("theoretical_cy"))
        if actual is not None and theoretical is not None and actual + 1e-6 < theoretical and not p.get("short_volume_approved"):
            return GateResult(self.name, "HOLD", f"Volume {actual}cy < theoretical {theoretical}cy", {"concrete": p})
        if not p.get("tickets_logged"):
            return GateResult(self.name, "HOLD", "Concrete tickets/slump not logged", {"concrete": p})
        return GateResult(self.name, "PASS", "Concrete placement clear", {"concrete": p})


class PileDrivingAgent:
    name = "pile-driving"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("driving") or {}
        if p.get("required") is False:
            return GateResult(self.name, "SKIP", "No driven pile this gate", {})
        if p.get("damaged"):
            return GateResult(self.name, "HOLD", "Pile damage indicators — stop and evaluate", {"driving": p})
        if p.get("refusal_short") and not p.get("eng_direction"):
            return GateResult(self.name, "HOLD", "Refusal short of tip without engineer direction", {"driving": p})
        if p.get("criteria_met") is False:
            return GateResult(self.name, "HOLD", "Driving criteria (blows/set/energy) not met", {"driving": p})
        return GateResult(self.name, "PASS", "Driven pile criteria clear", {"driving": p})


class IntegrityTestingAgent:
    name = "integrity-testing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        i = ctx.get("integrity") or {}
        if i.get("required") is False:
            return GateResult(self.name, "PASS", "Integrity testing not required", {"integrity": i})
        if not i.get("tests_complete"):
            return GateResult(self.name, "HOLD", "Required integrity tests incomplete", {"integrity": i})
        if i.get("open_anomalies"):
            return GateResult(self.name, "HOLD", "Integrity anomalies open: " + ", ".join(i["open_anomalies"]), {"integrity": i})
        return GateResult(self.name, "PASS", "Integrity testing clear", {"integrity": i})


class CapacityAcceptanceAgent:
    name = "capacity-acceptance"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("capacity") or {}
        if c.get("required") is False:
            return GateResult(self.name, "PASS", "Capacity gate not required", {"capacity": c})
        if not c.get("criteria_met"):
            return GateResult(self.name, "HOLD", "Capacity criteria not demonstrated", {"capacity": c})
        if c.get("rejects_open"):
            return GateResult(self.name, "HOLD", "Rejected elements not replaced/dispositioned", {"capacity": c})
        return GateResult(self.name, "PASS", "Capacity acceptance clear", {"capacity": c})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        holds = []
        if w.get("lightning") or w.get("high_wind"):
            holds.append("lightning/high wind — crane/drill/drive hold")
        if w.get("freezing") and not w.get("cold_weather_concrete"):
            holds.append("freeze risk without cold-weather concrete procedures")
        if w.get("flooding_holes") and not w.get("casing_control"):
            holds.append("flooding of open holes without casing/control")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/protection CLEAR", {"weather": w})


class GeotechAgent:
    name = "geotech"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("geotech") or {}
        if g.get("required") is False:
            return GateResult(self.name, "PASS", "Geotech hold not required this gate", {"geotech": g})
        if not g.get("tip_confirmed") and ctx.get("require_tip_si"):
            return GateResult(self.name, "HOLD", "Geotech tip/stratum confirmation missing", {"geotech": g})
        if not g.get("accepted"):
            return GateResult(self.name, "HOLD", "Geotech/SI acceptance missing", {"geotech": g})
        return GateResult(self.name, "PASS", "Geotech hold points clear", {"geotech": g})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("hole", {}).get("unprotected"):
            violations.append("unprotected open shaft/pile hole")
        if ctx.get("utilities", {}).get("dig_without_locate") or ctx.get("utilities", {}).get("utility_strike"):
            violations.append("drill/drive without locate or utility strike")
        if ctx.get("rigging", {}).get("unsafe"):
            violations.append("crane/rigging unsafe")
        if ctx.get("casing_slurry", {}).get("personnel_exposure_collapse"):
            violations.append("cave-in/slurry loss with personnel exposure")
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
            return GateResult(self.name, "PASS", "Pre-foundation QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class FoundationsLeadAgent:
    name = "foundations-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked deep foundation work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('element_id', 'element'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
