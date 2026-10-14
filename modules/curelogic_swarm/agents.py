"""Deterministic specialist gates for CureLogic curing."""
from __future__ import annotations
from typing import Any
from modules.curelogic_swarm.schemas import GateResult
ERECT_ROLES = ('cure_lead', 'pour_boss', 'finish_foreman', 'cure_tech', 'maturity_tech', 'qc_tech', 'safety_watch')

def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class CurePlanAgent:
    name = "cure-plan"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("plan") or {}
        if not p.get("method"):
            return GateResult(self.name, "HOLD", "Curing method not selected", {"plan": p})
        if p.get("approved") is False:
            return GateResult(self.name, "HOLD", "Curing plan not approved", {"plan": p})
        if not p.get("duration_days"):
            return GateResult(self.name, "HOLD", "Cure duration not specified", {"plan": p})
        return GateResult(self.name, "PASS", f"Cure plan clear ({p.get('method')})", {"plan": p})

class MoistureEnvelopeAgent:
    name = "moisture-envelope"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("moisture") or {}
        w = ctx.get("weather") or {}
        rh = _num(w.get("rh_pct"))
        rate = _num((ctx.get("evap") or {}).get("rate_g_m2_hr"), 0) or 0
        if m.get("protection_active") is False and rh is not None and rh < 30:
            return GateResult(self.name, "HOLD", "No moisture protection in dry ambient", {"moisture": m, "weather": w})
        if m.get("below_dewpoint_risk") and not m.get("protection_active"):
            return GateResult(self.name, "HOLD", "Dew-point/condensation risk without protection", {"moisture": m})
        if m.get("protection_active") is False and rate >= 0.5:
            return GateResult(self.name, "HOLD", "Moisture protection inactive under medium/high evap", {"moisture": m})
        return GateResult(self.name, "PASS", "Moisture envelope clear", {"moisture": m})

class EvaporationRateAgent:
    name = "evaporation-rate"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("evap") or {}
        rate = _num(e.get("rate_g_m2_hr"))
        if rate is None:
            return GateResult(self.name, "HOLD", "Evaporation rate not calculated", {"evap": e})
        controls = bool(e.get("aggressive_controls") or e.get("pour_delayed"))
        if rate > 1.0 and not controls:
            return GateResult(self.name, "FAIL", f"EvapRate Critical {rate} g/m2/hr without controls", {"evap": e})
        if rate >= 0.5 and not (e.get("cover_or_mist") or controls):
            return GateResult(self.name, "HOLD", f"Medium evap {rate} — need cover/mist", {"evap": e})
        return GateResult(self.name, "PASS", f"Evaporation clear ({rate} g/m2/hr)", {"evap": e})

class ThermalDeltaAgent:
    name = "thermal-delta"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("thermal") or {}
        core = _num(t.get("core_c")); surface = _num(t.get("surface_c"))
        limit = _num(t.get("delta_limit_c"), 20.0) or 20.0
        peak_limit = _num(t.get("peak_limit_c"), 75.0) or 75.0
        if core is None or surface is None:
            if t.get("monitored") is False:
                return GateResult(self.name, "HOLD", "Thermal monitoring not active", {"thermal": t})
            return GateResult(self.name, "PASS", "Thermal readings deferred / N/A", {"thermal": t})
        delta = abs(core - surface)
        mitigated = bool(t.get("insulation_active") or t.get("mitigated"))
        if core > peak_limit and not mitigated:
            return GateResult(self.name, "FAIL", f"Peak core {core}C > limit {peak_limit}C", {"thermal": t, "delta_c": delta})
        if delta > limit and not mitigated:
            return GateResult(self.name, "FAIL", f"Thermal Crack Risk ΔT {delta:.1f}C > {limit}C", {"thermal": t, "delta_c": delta})
        if delta > limit and mitigated:
            return GateResult(self.name, "PASS", f"ΔT {delta:.1f}C mitigated with insulation", {"thermal": t})
        return GateResult(self.name, "PASS", f"Thermal envelope clear (ΔT {delta:.1f}C)", {"thermal": t})

class AmbientWeatherAgent:
    name = "ambient-weather"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No ambient weather data", {})
        wind = _num(w.get("wind_kmh")); rh = _num(w.get("rh_pct"))
        method = (ctx.get("plan") or {}).get("method")
        if wind is not None and wind > 25 and method in ("fog", "spray_fogging") and not w.get("method_switched"):
            return GateResult(self.name, "FAIL", f"Fog Ineffective — wind {wind} km/h", {"weather": w})
        if rh is not None and rh < 30 and w.get("rh_low_hours", 0) >= 2 and not (ctx.get("moisture") or {}).get("protection_active"):
            return GateResult(self.name, "HOLD", "Ambient Too Dry >2 hr without aggressive moist cure", {"weather": w})
        return GateResult(self.name, "PASS", "Ambient weather CLEAR for curing", {"weather": w})

class WetCureAgent:
    name = "wet-cure"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        method = (ctx.get("plan") or {}).get("method")
        if method not in ("wet_burlap", "fog", "spray_fogging", "wet"):
            return GateResult(self.name, "SKIP", "Wet cure not the active method", {})
        c = ctx.get("wet") or {}
        if c.get("saturated") is False:
            return GateResult(self.name, "HOLD", "Burlap/wet media not kept saturated", {"wet": c})
        if c.get("continuous") is False:
            return GateResult(self.name, "HOLD", "Wet cure coverage interrupted", {"wet": c})
        return GateResult(self.name, "PASS", "Wet cure clear", {"wet": c})

class MembraneCompoundAgent:
    name = "membrane-compound"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        method = (ctx.get("plan") or {}).get("method")
        if method not in ("membrane", "compound", "curing_compound"):
            return GateResult(self.name, "SKIP", "Membrane compound not the active method", {})
        m = ctx.get("membrane") or {}
        if not m.get("logged"):
            return GateResult(self.name, "HOLD", "CureCompound Unlogged — spray log missing", {"membrane": m})
        if m.get("coverage_ok") is False or m.get("dry_spots"):
            return GateResult(self.name, "HOLD", "Compound coverage incomplete / dry spots", {"membrane": m})
        if m.get("astm_c309") is False:
            return GateResult(self.name, "HOLD", "Compound not ASTM C309 / spec compliant", {"membrane": m})
        return GateResult(self.name, "PASS", "Membrane compound clear", {"membrane": m})

class CoverBlanketAgent:
    name = "cover-blanket"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        method = (ctx.get("plan") or {}).get("method")
        c = ctx.get("cover") or {}
        if method not in ("poly_cover", "blanket", "cover", "insulation") and not c.get("required"):
            return GateResult(self.name, "SKIP", "Cover/blanket not required", {})
        if c.get("lifted") or c.get("edges_sealed") is False:
            return GateResult(self.name, "HOLD", "Cover lifted or edges not sealed", {"cover": c})
        temp = _num((ctx.get("weather") or {}).get("temp_c"), 20) or 20
        if c.get("cold_rated") is False and temp < 10:
            return GateResult(self.name, "HOLD", "Blanket not thermal-rated for cold ambient", {"cover": c})
        return GateResult(self.name, "PASS", "Cover/blanket clear", {"cover": c})

class MaturityStrengthAgent:
    name = "maturity-strength"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("maturity") or {}
        if m.get("release_requested") is False and m.get("required") is False:
            return GateResult(self.name, "SKIP", "No strength release requested", {})
        if not m.get("proof"):
            return GateResult(self.name, "FAIL", "No maturity/cylinder proof for release", {"maturity": m})
        strength = _num(m.get("strength_pct")); min_pct = _num(m.get("min_strength_pct"), 70.0) or 70.0
        if strength is not None and strength < min_pct:
            return GateResult(self.name, "FAIL", f"Strength {strength}% < min {min_pct}% for release", {"maturity": m})
        return GateResult(self.name, "PASS", "Maturity/strength clear for release", {"maturity": m})

class ColdWeatherCureAgent:
    name = "cold-weather-cure"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}; c = ctx.get("cold") or {}
        temp = _num(w.get("temp_c"))
        if (temp is None or temp >= 10) and not c.get("required"):
            return GateResult(self.name, "SKIP", "Cold-weather cure not required", {})
        if temp is not None and temp < 5 and not c.get("protection_active"):
            return GateResult(self.name, "FAIL", f"Freezing/cold risk at {temp}C without protection", {"weather": w, "cold": c})
        if temp is not None and temp < 10 and not c.get("protection_active"):
            return GateResult(self.name, "HOLD", "Cold ambient — protection/blankets required", {"weather": w, "cold": c})
        return GateResult(self.name, "PASS", "Cold-weather curing clear", {"cold": c})

class HotWeatherCureAgent:
    name = "hot-weather-cure"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        h = ctx.get("hot") or {}; e = ctx.get("evap") or {}
        rate = _num(e.get("rate_g_m2_hr"), 0) or 0
        if rate < 0.5 and not h.get("required"):
            return GateResult(self.name, "SKIP", "Hot-weather extras not required", {})
        if rate > 1.0 and not (h.get("controls_staged") or e.get("aggressive_controls") or e.get("pour_delayed")):
            return GateResult(self.name, "FAIL", "Hot-weather critical evap without controls", {"hot": h, "evap": e})
        if rate >= 0.5 and not (h.get("controls_staged") or e.get("cover_or_mist")):
            return GateResult(self.name, "HOLD", "Hot-weather controls not staged for finishing", {"hot": h})
        return GateResult(self.name, "PASS", "Hot-weather curing clear", {"hot": h})

class SteamAccelAgent:
    name = "steam-accel"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        method = (ctx.get("plan") or {}).get("method"); s = ctx.get("steam") or {}
        if method not in ("steam", "heated_enclosure", "accelerated") and not s.get("required"):
            return GateResult(self.name, "SKIP", "Steam/accelerated curing not active", {})
        ramp = _num(s.get("ramp_c_per_hr")); peak = _num(s.get("peak_c"))
        if ramp is not None and ramp > 20:
            return GateResult(self.name, "FAIL", f"Steam ramp {ramp}C/hr > 20C/hr", {"steam": s})
        if peak is not None and peak > (_num(s.get("max_c"), 70) or 70):
            return GateResult(self.name, "FAIL", f"Steam peak {peak}C exceeds max", {"steam": s})
        if not s.get("logged"):
            return GateResult(self.name, "HOLD", "Steam temp log incomplete", {"steam": s})
        return GateResult(self.name, "PASS", "Steam/accelerated curing clear", {"steam": s})

class SafetyFailsafeAgent:
    name = "safety-failsafe"
    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}; violations = list(s.get("violations") or [])
        e = ctx.get("evap") or {}; rate = _num(e.get("rate_g_m2_hr"))
        if rate is not None and rate > 1.0 and not (e.get("aggressive_controls") or e.get("pour_delayed")):
            violations.append("critical evaporation without controls")
        t = ctx.get("thermal") or {}; core = _num(t.get("core_c")); surface = _num(t.get("surface_c"))
        limit = _num(t.get("delta_limit_c"), 20.0) or 20.0
        if core is not None and surface is not None and abs(core - surface) > limit and not (t.get("insulation_active") or t.get("mitigated")):
            violations.append("thermal crack risk ΔT exceeded")
        peak_limit = _num(t.get("peak_limit_c"), 75.0) or 75.0
        if core is not None and core > peak_limit and not (t.get("insulation_active") or t.get("mitigated")):
            violations.append("peak core temperature exceeded")
        w = ctx.get("weather") or {}; temp = _num(w.get("temp_c"))
        if temp is not None and temp < 5 and not (ctx.get("cold") or {}).get("protection_active"):
            violations.append("freezing risk on unprotected early-age concrete")
        method = (ctx.get("plan") or {}).get("method")
        if method in ("fog", "spray_fogging") and (_num(w.get("wind_kmh")) or 0) > 25 and not w.get("method_switched"):
            violations.append("fog ineffective in high wind")
        m = ctx.get("maturity") or {}
        if (m.get("release_requested") or m.get("required")) and not m.get("proof"):
            violations.append("premature release without strength proof")
        strength = _num(m.get("strength_pct")); min_pct = _num(m.get("min_strength_pct"), 70.0) or 70.0
        if (m.get("release_requested") or m.get("required")) and strength is not None and strength < min_pct and m.get("proof"):
            violations.append("premature release below min strength")
        st = ctx.get("steam") or {}
        if (_num(st.get("ramp_c_per_hr")) or 0) > 20:
            violations.append("steam ramp exceeded")
        if (_num(st.get("peak_c")) or 0) > (_num(st.get("max_c"), 70) or 70):
            violations.append("steam peak exceeded")
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
            return GateResult(self.name, "HOLD", "Cure briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Cure crew ready headcount={crew.get('headcount', len(roles))}", {})

class QaInspectorAgent:
    name = "qa-inspector"
    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-cure docs clear", {})
        if phase == "release" and q.get("release_docs_clear"):
            return GateResult(self.name, "PASS", "Release/maturity docs clear", {})
        if phase not in ("pre",) and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} cure docs clear", {})
        return GateResult(self.name, "HOLD", f"No curing QA evidence for phase={phase}", {"qa": q})

class CureLeadAgent:
    name = "cure-lead"
    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked curing sequence"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Curing sequence ready for {ctx.get('zone_id', ctx.get('pour_id', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
