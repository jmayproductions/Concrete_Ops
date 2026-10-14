"""Deterministic specialist gates for precast / panelized erection."""

from __future__ import annotations

from typing import Any

from modules.precast_swarm.schemas import GateResult

DEFAULT_WIND_HOLD_KPH = 40.0
ERECT_ROLES = ('precast_lead', 'crane_operator', 'rigger', 'connector', 'brace_crew', 'qc_tech', 'safety_watch')


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class FabReleaseAgent:
    name = "fab-release"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("fab") or {}
        miss = _missing(f, ("shops_approved", "embeds_verified", "strength_released"))
        if miss:
            return GateResult(self.name, "HOLD", "Fab release incomplete: " + ", ".join(miss), {"fab": f})
        strength_pct = _num(f.get("strength_pct_design"))
        min_pct = _num(f.get("min_strength_pct"), 75) or 75
        if strength_pct is not None and strength_pct < min_pct:
            return GateResult(self.name, "HOLD", f"Strength {strength_pct}% < {min_pct}% — early release blocked", {"fab": f})
        if f.get("shipping_damage"):
            return GateResult(self.name, "HOLD", "Shipping/handling damage on panel(s)", {"fab": f})
        return GateResult(self.name, "PASS", "Fab/strength release clear", {"fab": f})


class PanelSupplyAgent:
    name = "panel-supply"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("supply") or {}
        if not s.get("sequence_published"):
            return GateResult(self.name, "HOLD", "Erection sequence not published", {"supply": s})
        truck = s.get("truck") or {}
        if truck:
            expected = set(truck.get("expected_panel_tags") or [])
            onboard = set(truck.get("onboard_panel_tags") or [])
            if expected and onboard != expected:
                return GateResult(self.name, "HOLD", f"Panel tags mismatch expected={sorted(expected)} got={sorted(onboard)}", {"truck": truck})
        return GateResult(self.name, "PASS", "Panel supply/sequence clear", {"supply": s})


class SurveyEmbedsAgent:
    name = "survey-embeds"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("survey") or {}
        if not s:
            return GateResult(self.name, "HOLD", "No survey/embed package", {})
        if s.get("within_tolerance") is False:
            return GateResult(self.name, "FAIL", f"Supports/embeds out of tolerance: {s.get('notes', 'see survey')}", {"survey": s})
        if s.get("embed_clash"):
            return GateResult(self.name, "HOLD", "Embed clash — redesign/resolve before lift", {"survey": s})
        miss = _missing(s, ("haunches_verified", "grid_control"))
        if miss:
            return GateResult(self.name, "HOLD", "Survey incomplete: " + ", ".join(miss), {"survey": s})
        return GateResult(self.name, "PASS", "Survey/embeds within tolerance", {"survey": s})


class CraneRiggingAgent:
    name = "crane-rigging"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("crane") or {}
        miss = _missing(c, ("chart_ok", "lift_plan_verified", "exclusion_zone_set", "inserts_verified"))
        if miss:
            return GateResult(self.name, "HOLD", "Crane/rigging incomplete: " + ", ".join(miss), {"crane": c})
        if c.get("overload"):
            return GateResult(self.name, "FAIL", "Crane overload indicated", {"crane": c})
        if c.get("camber_mismatch"):
            return GateResult(self.name, "HOLD", "Panel camber mismatch beyond lift limit", {"crane": c})
        return GateResult(self.name, "PASS", "Crane/rigging clear", {"crane": c})


class TempBracingAgent:
    name = "temp-bracing"

    def plan(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bracing") or {}
        if not b.get("plan_issued"):
            return GateResult(self.name, "HOLD", "Temporary brace plan not issued", {"bracing": b})
        return GateResult(self.name, "PASS", "Brace plan issued", {"bracing": b})

    def lock_in(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bracing") or {}
        if b.get("unstable_without_brace"):
            return GateResult(self.name, "FAIL", "Unstable panel without required braces", {"bracing": b})
        if not b.get("braces_installed"):
            return GateResult(self.name, "HOLD", "Required erection braces not installed", {"bracing": b})
        return GateResult(self.name, "PASS", "Temporary bracing locked", {"bracing": b})


class PanelSetAgent:
    name = "panel-set"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("panels") or {}
        if not p.get("seated"):
            return GateResult(self.name, "HOLD", "Panels not seated per shops", {"panels": p})
        if p.get("force_fit"):
            return GateResult(self.name, "HOLD", "Force-fit attempted — stop and re-survey", {"panels": p})
        if p.get("within_plumb") is False:
            return GateResult(self.name, "HOLD", "Panel plumb/alignment out of tolerance", {"panels": p})
        return GateResult(self.name, "PASS", "Panel set clear", {"panels": p})


class ConnectionsAgent:
    name = "connections"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("connections") or {}
        if not c.get("hardware_matched"):
            return GateResult(self.name, "HOLD", "Connection hardware not matched to panel tags", {"connections": c})
        incomplete = list(c.get("incomplete_patterns") or [])
        if incomplete:
            return GateResult(self.name, "HOLD", "Incomplete connections: " + ", ".join(incomplete), {"connections": c})
        if c.get("structural_failure"):
            return GateResult(self.name, "FAIL", "Structural connection failure reported", {"connections": c})
        return GateResult(self.name, "PASS", "Connections clear", {"connections": c})


class GroutJointsAgent:
    name = "grout-joints"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("grout") or {}
        if g.get("required") is False:
            return GateResult(self.name, "PASS", "Joint grout not required this gate", {"grout": g})
        if not g.get("materials_approved"):
            return GateResult(self.name, "HOLD", "Grout materials not approved", {"grout": g})
        if g.get("complete") is False:
            return GateResult(self.name, "HOLD", "Required joint grout incomplete", {"grout": g})
        return GateResult(self.name, "PASS", "Grout/joints clear", {"grout": g})


class HybridInterfaceAgent:
    name = "hybrid-interface"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        h = ctx.get("hybrid") or {}
        if h.get("required") is False:
            return GateResult(self.name, "PASS", "No hybrid interface this zone", {"hybrid": h})
        miss = _missing(h, ("interface_released", "bearing_details_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Hybrid interface incomplete: " + ", ".join(miss), {"hybrid": h})
        return GateResult(self.name, "PASS", "Hybrid interface released", {"hybrid": h})


class FinishProtectAgent:
    name = "finish-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("finish") or {}
        if f.get("architectural") and not f.get("protection_plan"):
            return GateResult(self.name, "HOLD", "Architectural finish protection missing", {"finish": f})
        if f.get("padded_rigging") is False:
            return GateResult(self.name, "HOLD", "Padded/non-marring rigging not confirmed", {"finish": f})
        return GateResult(self.name, "PASS", "Finish protection clear", {"finish": f})


class BraceReleaseAgent:
    name = "brace-release"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("brace_release") or {}
        if b.get("unstable"):
            return GateResult(self.name, "FAIL", "Brace release blocked — panel still unstable", {"brace_release": b})
        miss = _missing(b, ("permanent_connections_complete", "criteria_met"))
        if miss:
            return GateResult(self.name, "HOLD", "Brace release incomplete: " + ", ".join(miss), {"brace_release": b})
        return GateResult(self.name, "PASS", "Brace release clear", {"brace_release": b})


class WeatherGateAgent:
    name = "weather-gate"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        wind = _num(w.get("wind_kph"), 0) or 0
        limit = _num(w.get("wind_hold_kph"), DEFAULT_WIND_HOLD_KPH) or DEFAULT_WIND_HOLD_KPH
        holds = []
        if wind >= limit:
            holds.append(f"wind {wind}kph ≥ {limit}kph")
        if w.get("lightning"):
            holds.append("lightning/storm")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", f"Weather CLEAR wind={wind}kph", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("bracing", {}).get("unstable_without_brace"):
            violations.append("unstable panel without brace")
        if ctx.get("crane", {}).get("overload"):
            violations.append("crane overload")
        if ctx.get("brace_release", {}).get("unstable"):
            violations.append("brace removal on unstable panel")
        if ctx.get("connections", {}).get("structural_failure"):
            violations.append("structural connection failure")
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
            return GateResult(self.name, "HOLD", "Lift briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Crew ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-erect QA hold points clear", {})
        if phase != "pre" and q.get("lift_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class PrecastLeadAgent:
    name = "precast-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked panel erection"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('erect_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
