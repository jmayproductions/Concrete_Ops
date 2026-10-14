"""Deterministic specialist gates for envelope / waterproofing."""

from __future__ import annotations

from typing import Any

from modules.envelope_swarm.schemas import GateResult

DEFAULT_MEMBRANE_MIN_F = 40.0
DEFAULT_WIND_HOLD_KPH = 50.0
ERECT_ROLES = ('envelope_lead', 'membrane_tech', 'flashing_tech', 'sealant_tech', 'qc_tech', 'safety_watch')


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class SubstratePrepAgent:
    name = "substrate-prep"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("substrate") or {}
        miss = _missing(s, ("clean", "dry"))
        if miss:
            return GateResult(self.name, "HOLD", "Substrate not ready: " + ", ".join(miss), {"substrate": s})
        if s.get("cured") is False:
            return GateResult(self.name, "HOLD", "Concrete/substrate not cured for membrane", {"substrate": s})
        if s.get("slope_ok") is False:
            return GateResult(self.name, "HOLD", "Slope to drain not verified", {"substrate": s})
        if s.get("voids_patched") is False:
            return GateResult(self.name, "HOLD", "Voids/honeycombs not patched", {"substrate": s})
        return GateResult(self.name, "PASS", "Substrate ready", {"substrate": s})


class WeatherBarrierAgent:
    name = "weather-barrier"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("wrb") or {}
        if not w and not ctx.get("require_wrb"):
            return GateResult(self.name, "SKIP", "No WRB scope", {})
        miss = _missing(w, ("installed", "laps_sealed", "transitions_detailed"))
        if miss:
            return GateResult(self.name, "HOLD", "WRB incomplete: " + ", ".join(miss), {"wrb": w})
        if w.get("open_deficiencies"):
            return GateResult(self.name, "HOLD", "Open WRB deficiencies: " + ", ".join(w["open_deficiencies"]), {"wrb": w})
        return GateResult(self.name, "PASS", "WRB/air barrier continuity clear", {"wrb": w})


class BelowGradeWpAgent:
    name = "below-grade-wp"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("below_grade") or {}
        if not b and not ctx.get("require_below_grade"):
            return GateResult(self.name, "SKIP", "No below-grade WP scope", {})
        miss = _missing(b, ("membrane_installed", "laps_sealed", "no_pinholes"))
        if miss:
            return GateResult(self.name, "HOLD", "Below-grade WP incomplete: " + ", ".join(miss), {"below_grade": b})
        mils = _num(b.get("wet_film_mils"))
        min_mils = _num(b.get("min_mils"), 60) or 60
        if mils is not None and mils < min_mils:
            return GateResult(self.name, "HOLD", f"Wet film {mils} mils < {min_mils}", {"below_grade": b})
        if not b.get("protection_board"):
            return GateResult(self.name, "HOLD", "Protection board/drainage not installed before backfill", {"below_grade": b})
        return GateResult(self.name, "PASS", "Below-grade WP clear", {"below_grade": b})


class RoofingMembraneAgent:
    name = "roofing-membrane"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        r = ctx.get("roofing") or {}
        if not r and not ctx.get("require_roofing"):
            return GateResult(self.name, "SKIP", "No roofing scope", {})
        miss = _missing(r, ("primer_ok", "laps_ok", "seams_accepted"))
        if miss:
            return GateResult(self.name, "HOLD", "Roofing incomplete: " + ", ".join(miss), {"roofing": r})
        if r.get("seam_pull_fail"):
            return GateResult(self.name, "FAIL", "Seam pull test failed", {"roofing": r})
        return GateResult(self.name, "PASS", "Roofing membrane clear", {"roofing": r})


class FlashingPenetrationsAgent:
    name = "flashing-penetrations"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("flashing") or {}
        miss = _missing(f, ("penetrations_flashed", "terminations_complete"))
        if miss:
            return GateResult(self.name, "HOLD", "Flashing incomplete: " + ", ".join(miss), {"flashing": f})
        if f.get("critical_missing"):
            return GateResult(self.name, "FAIL", "Critical flashing missing: " + ", ".join(f["critical_missing"]), {"flashing": f})
        return GateResult(self.name, "PASS", "Flashings/penetrations clear", {"flashing": f})


class CurtainWallAgent:
    name = "curtain-wall"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("curtain_wall") or {}
        if not c and not ctx.get("require_curtain_wall"):
            return GateResult(self.name, "SKIP", "No curtain wall scope", {})
        miss = _missing(c, ("setting_blocks_ok", "perimeter_sealed", "anchorage_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Curtain wall incomplete: " + ", ".join(miss), {"curtain_wall": c})
        return GateResult(self.name, "PASS", "Curtain wall install clear", {"curtain_wall": c})


class CladdingRainscreenAgent:
    name = "cladding-rainscreen"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("cladding") or {}
        if not c and not ctx.get("require_cladding"):
            return GateResult(self.name, "SKIP", "No cladding scope", {})
        if not c.get("wrb_accepted"):
            return GateResult(self.name, "HOLD", "WRB not accepted before cladding", {"cladding": c})
        miss = _missing(c, ("drainage_cavity_clear", "weeps_open", "flashings_integrated"))
        if miss:
            return GateResult(self.name, "HOLD", "Cladding incomplete: " + ", ".join(miss), {"cladding": c})
        return GateResult(self.name, "PASS", "Cladding/rainscreen clear", {"cladding": c})


class SealantsAgent:
    name = "sealants"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("sealants") or {}
        if not s:
            return GateResult(self.name, "SKIP", "No sealant scope", {})
        miss = _missing(s, ("joints_prepped", "tooled"))
        if miss:
            return GateResult(self.name, "HOLD", "Sealants incomplete: " + ", ".join(miss), {"sealants": s})
        if s.get("adhesion_fail"):
            return GateResult(self.name, "HOLD", "Sealant adhesion test failed", {"sealants": s})
        if s.get("weeps_blocked"):
            return GateResult(self.name, "HOLD", "Sealant blocking weeps/drainage", {"sealants": s})
        return GateResult(self.name, "PASS", "Sealants clear", {"sealants": s})


class WaterTestAgent:
    name = "water-test"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("water_test") or {}
        if t.get("required") is False:
            return GateResult(self.name, "PASS", "Water test not required this gate", {"water_test": t})
        if not t.get("performed"):
            return GateResult(self.name, "HOLD", "Required water test not performed", {"water_test": t})
        if t.get("passed") is False:
            return GateResult(self.name, "FAIL", f"Water test failed: {t.get('notes', 'leakage')}", {"water_test": t})
        return GateResult(self.name, "PASS", "Water test passed", {"water_test": t})


class AirBarrierTestAgent:
    name = "air-barrier-test"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("air_test") or {}
        if t.get("required") is False:
            return GateResult(self.name, "PASS", "Air test not required this gate", {"air_test": t})
        if not t.get("performed"):
            return GateResult(self.name, "HOLD", "Required air barrier test not performed", {"air_test": t})
        if t.get("passed") is False:
            return GateResult(self.name, "HOLD", f"Air leakage above target: {t.get('notes', 'see report')}", {"air_test": t})
        return GateResult(self.name, "PASS", "Air barrier test clear", {"air_test": t})


class DrainageProtectionAgent:
    name = "drainage-protection"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("drainage") or {}
        if not d:
            return GateResult(self.name, "SKIP", "No drainage/protection scope", {})
        if d.get("standing_water"):
            return GateResult(self.name, "HOLD", "Standing water on membrane", {"drainage": d})
        if d.get("requires_protection") and not d.get("protection_installed"):
            return GateResult(self.name, "HOLD", "Protection/drainage composite missing", {"drainage": d})
        if d.get("drains_clear") is False:
            return GateResult(self.name, "HOLD", "Drains/scuppers not clear/flashed", {"drainage": d})
        return GateResult(self.name, "PASS", "Drainage/protection clear", {"drainage": d})


class WeatherGateAgent:
    name = "weather-gate"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        temp = _num(w.get("temp_f"))
        min_f = _num(w.get("membrane_min_f"), DEFAULT_MEMBRANE_MIN_F) or DEFAULT_MEMBRANE_MIN_F
        wind = _num(w.get("wind_kph"), 0) or 0
        limit = _num(w.get("wind_hold_kph"), DEFAULT_WIND_HOLD_KPH) or DEFAULT_WIND_HOLD_KPH
        holds: list[str] = []
        if temp is not None and temp < min_f:
            holds.append(f"temp {temp}F < {min_f}F")
        if wind >= limit:
            holds.append(f"wind {wind}kph ≥ {limit}kph")
        if w.get("active_precip") and not w.get("shelter"):
            holds.append("active precip without shelter")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", f"Weather CLEAR temp={temp}F wind={wind}kph", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("roofing", {}).get("torch_unsafe"):
            violations.append("unsafe torch/hot-work conditions")
        if ctx.get("below_grade", {}).get("backfill_without_protection"):
            violations.append("backfill against unprotected waterproofing")
        if violations:
            return GateResult(self.name, "FAIL", "STOP-WORK: " + "; ".join(violations), {"violations": violations})
        return GateResult(self.name, "PASS", "No fail-safe violations", {})


class CrewOpsAgent:
    name = "crew-ops"

    def evaluate(self, ctx: dict[str, Any], require_briefing: bool = True) -> GateResult:
        crew = ctx.get("crew") or {}
        roles = set(crew.get("roles") or [])
        required = list(ERECT_ROLES)
        if (ctx.get("curtain_wall") or {}).get("required"):
            if "glazier" not in roles:
                required.append("glazier")
        missing = [r for r in required if r not in roles]
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
            return GateResult(self.name, "PASS", "Pre-install QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        checks = [c for c in (q.get("checks") or []) if c.get("phase", "pre") == phase]
        if not checks:
            return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})
        failed = [c for c in checks if not c.get("passed")]
        if failed:
            return GateResult(self.name, "FAIL", "QA failed: " + "; ".join(c.get("description", "check") for c in failed), {"failed": failed})
        return GateResult(self.name, "PASS", f"QA {len(checks)} checks passed", {})


class EnvelopeLeadAgent:
    name = "envelope-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked envelope work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
