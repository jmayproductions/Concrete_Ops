"""Deterministic specialist gates for masonry construction."""

from __future__ import annotations

from typing import Any

from modules.masonry_swarm.schemas import GateResult

ERECT_ROLES = ('masonry_lead', 'mason', 'tender', 'rebar_setter', 'grout_tech', 'qc_tech', 'safety_watch')
DEFAULT_MAX_GROUT_LIFT_FT = 5.0


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class MaterialsSubmittalAgent:
    name = "materials-submittal"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("materials") or {}
        miss = _missing(m, ("mortar_approved", "grout_approved", "units_certified", "rebar_approved"))
        if miss:
            return GateResult(self.name, "HOLD", "Materials incomplete: " + ", ".join(miss), {"materials": m})
        return GateResult(self.name, "PASS", "Mortar/grout/units/rebar submittals clear", {"materials": m})


class LayoutCoursingAgent:
    name = "layout-coursing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("layout") or {}
        miss = _missing(l, ("control_lines", "coursing_set", "bond_confirmed"))
        if miss:
            return GateResult(self.name, "HOLD", "Layout incomplete: " + ", ".join(miss), {"layout": l})
        if l.get("drift_over_limit"):
            return GateResult(self.name, "HOLD", "Bond/coursing drift over limit — rework", {"layout": l})
        return GateResult(self.name, "PASS", "Layout/coursing clear", {"layout": l})


class MortarQcAgent:
    name = "mortar-qc"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("mortar") or {}
        if m.get("consistency_ok") is False:
            return GateResult(self.name, "HOLD", "Mortar consistency out of spec", {"mortar": m})
        if m.get("joint_thickness_ok") is False:
            return GateResult(self.name, "HOLD", "Joint thickness out of tolerance", {"mortar": m})
        if not m.get("tooled"):
            return GateResult(self.name, "HOLD", "Joints not tooled/accepted", {"mortar": m})
        if m.get("retempered_expired"):
            return GateResult(self.name, "HOLD", "Retempered/expired mortar in use", {"mortar": m})
        return GateResult(self.name, "PASS", "Mortar QC clear", {"mortar": m})


class ReinforcementAgent:
    name = "reinforcement"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        r = ctx.get("rebar") or {}
        miss = _missing(r, ("spacing_ok", "clean", "laps_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Reinforcement incomplete: " + ", ".join(miss), {"rebar": r})
        return GateResult(self.name, "PASS", "Reinforcement clear", {"rebar": r})


class GroutLiftsAgent:
    name = "grout-lifts"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("grout") or {}
        if g.get("required") is False:
            return GateResult(self.name, "PASS", "No grout this gate", {"grout": g})
        lift = _num(g.get("lift_ft"))
        max_lift = _num(g.get("max_lift_ft"), DEFAULT_MAX_GROUT_LIFT_FT) or DEFAULT_MAX_GROUT_LIFT_FT
        if lift is not None and lift > max_lift:
            return GateResult(self.name, "HOLD", f"Grout lift {lift}ft > {max_lift}ft max", {"grout": g})
        if g.get("consolidated") is False:
            return GateResult(self.name, "HOLD", "Grout not consolidated / voids suspected", {"grout": g})
        if g.get("voids"):
            return GateResult(self.name, "HOLD", "Grout voids reported", {"grout": g})
        return GateResult(self.name, "PASS", "Grout lifts clear", {"grout": g})


class FlashingWeepsAgent:
    name = "flashing-weeps"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("flashing") or {}
        if not f.get("flashing_installed"):
            return GateResult(self.name, "HOLD", "Required through-wall flashing missing", {"flashing": f})
        if f.get("weeps_open") is False:
            return GateResult(self.name, "HOLD", "Weeps blocked or missing", {"flashing": f})
        if f.get("end_dams_ok") is False:
            return GateResult(self.name, "HOLD", "Flashing end dams/laps deficient", {"flashing": f})
        return GateResult(self.name, "PASS", "Flashing/weeps clear", {"flashing": f})


class PlumbToleranceAgent:
    name = "plumb-tolerance"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("plumb") or {}
        if p.get("within_tolerance") is False:
            return GateResult(self.name, "HOLD", f"Plumb/plane out of tolerance: {p.get('notes', 'see survey')}", {"plumb": p})
        if not p.get("checked"):
            return GateResult(self.name, "HOLD", "Plumb checks not recorded", {"plumb": p})
        return GateResult(self.name, "PASS", "Plumb/tolerance clear", {"plumb": p})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        holds = []
        if w.get("freezing") and not w.get("cold_weather_procedures"):
            holds.append("freezing without cold-weather procedures")
        if w.get("hot_dry") and not w.get("hot_weather_protection"):
            holds.append("hot/dry without curing protection")
        if w.get("active_precip") and not w.get("shelter"):
            holds.append("active precip without shelter")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/protection CLEAR", {"weather": w})


class CureProtectAgent:
    name = "cure-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("cure") or {}
        if c.get("required") is False:
            return GateResult(self.name, "PASS", "Cure protection not required", {"cure": c})
        if not c.get("protected"):
            return GateResult(self.name, "HOLD", "Green masonry not protected from drying/frost", {"cure": c})
        if c.get("early_load"):
            return GateResult(self.name, "HOLD", "Early load/backfill before cure criteria", {"cure": c})
        return GateResult(self.name, "PASS", "Cure/protection clear", {"cure": c})


class RainscreenVeneerAgent:
    name = "rainscreen-veneer"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        v = ctx.get("veneer") or {}
        if not v and not ctx.get("require_veneer"):
            return GateResult(self.name, "SKIP", "No veneer scope", {})
        if v.get("cavity_blocked"):
            return GateResult(self.name, "HOLD", "Veneer cavity blocked (moisture lock)", {"veneer": v})
        miss = _missing(v, ("ties_ok", "weeps_spaced_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Veneer incomplete: " + ", ".join(miss), {"veneer": v})
        return GateResult(self.name, "PASS", "Veneer/rainscreen clear", {"veneer": v})


class EmbedsAnchorsAgent:
    name = "embeds-anchors"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("embeds") or {}
        if not e:
            return GateResult(self.name, "SKIP", "No embeds scope", {})
        if e.get("missing_before_grout"):
            return GateResult(self.name, "HOLD", "Missing embeds in cells to be grouted: " + ", ".join(e["missing_before_grout"]), {"embeds": e})
        return GateResult(self.name, "PASS", "Embeds/anchors clear", {"embeds": e})


class ControlJointsAgent:
    name = "control-joints"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("control_joints") or {}
        if not c:
            return GateResult(self.name, "SKIP", "No control joint scope", {})
        if c.get("mortared_closed"):
            return GateResult(self.name, "HOLD", "Control joints mortared closed", {"control_joints": c})
        if not c.get("located_per_shops"):
            return GateResult(self.name, "HOLD", "Control joints not located per shops", {"control_joints": c})
        return GateResult(self.name, "PASS", "Control joints clear", {"control_joints": c})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("wall", {}).get("unstable_unbraced"):
            violations.append("unstable unbraced masonry wall")
        if ctx.get("scaffold", {}).get("unsafe"):
            violations.append("scaffold unsafe")
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
            return GateResult(self.name, "PASS", "Pre-masonry QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class MasonryLeadAgent:
    name = "masonry-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked masonry work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
