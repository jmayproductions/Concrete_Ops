"""Deterministic specialist gates for mass timber erection."""

from __future__ import annotations

from typing import Any

from modules.mass_timber_swarm.schemas import GateResult

DEFAULT_MC_MAX = 16.0
DEFAULT_WIND_HOLD_KPH = 40.0

ERECT_ROLES = (
    "erect_lead",
    "crane_operator",
    "rigger",
    "connector",
    "brace_crew",
    "qc_tech",
    "safety_watch",
)


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _missing_flags(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class SupplyChainAgent:
    name = "supply-chain"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("supply") or {}
        miss = _missing_flags(
            s,
            ("shop_drawings_approved", "erection_drawings_approved", "sequence_published", "cnc_complete"),
        )
        if miss:
            return GateResult(self.name, "HOLD", "Missing: " + ", ".join(miss), {"supply": s})
        truck = s.get("truck") or {}
        if truck:
            expected = set(truck.get("expected_piece_marks") or [])
            onboard = set(truck.get("onboard_piece_marks") or [])
            if expected and onboard != expected:
                return GateResult(
                    self.name,
                    "HOLD",
                    f"Truck piece marks mismatch expected={sorted(expected)} got={sorted(onboard)}",
                    {"truck": truck},
                )
        return GateResult(self.name, "PASS", "Shops/erection drawings/sequence ready", {"supply": s})


class SurveyToleranceAgent:
    name = "survey-tolerance"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        survey = ctx.get("survey") or {}
        if not survey:
            return GateResult(self.name, "HOLD", "No survey/as-built package", {})
        if survey.get("within_tolerance") is False:
            return GateResult(
                self.name,
                "FAIL",
                f"Supports/embeds out of tolerance: {survey.get('notes', 'see as-built')}",
                {"survey": survey},
            )
        miss = _missing_flags(survey, ("podium_asbuilt", "embeds_verified", "grid_control"))
        if miss:
            return GateResult(self.name, "HOLD", "Survey incomplete: " + ", ".join(miss), {"survey": survey})
        return GateResult(self.name, "PASS", "Survey within timber tolerance", {"survey": survey})


class CraneLogisticsAgent:
    name = "crane-logistics"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        crane = ctx.get("crane") or {}
        miss = _missing_flags(crane, ("chart_ok", "pick_points_verified", "exclusion_zone_set"))
        if miss:
            return GateResult(self.name, "HOLD", "Crane logistics incomplete: " + ", ".join(miss), {"crane": crane})
        if crane.get("trailer_direct") is False and not crane.get("marshalling_planned"):
            return GateResult(self.name, "HOLD", "No trailer-direct path and no marshalling plan", {"crane": crane})
        return GateResult(self.name, "PASS", "Crane/logistics clear", {"crane": crane})


class MoistureProtectAgent:
    name = "moisture-protect"

    def plan_ready(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("moisture") or {}
        if not m.get("mmp_approved"):
            return GateResult(self.name, "HOLD", "Moisture Management Plan not approved", {"moisture": m})
        if not m.get("protection_materials_staged"):
            return GateResult(self.name, "HOLD", "Protection materials not staged", {"moisture": m})
        return GateResult(self.name, "PASS", "MMP ready", {"moisture": m})

    def daily(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("moisture") or {}
        mc = _num(m.get("moisture_content_pct"))
        limit = _num(m.get("max_mc_pct"), DEFAULT_MC_MAX) or DEFAULT_MC_MAX
        issues: list[str] = []
        if mc is None:
            issues.append("no MC reading")
        elif mc > limit:
            issues.append(f"MC {mc}% > {limit}%")
        if m.get("standing_water"):
            issues.append("standing water present")
        if m.get("joints_sealed") is False:
            issues.append("joints not sealed")
        if issues:
            return GateResult(self.name, "HOLD", "; ".join(issues), {"moisture": m})
        return GateResult(self.name, "PASS", f"Moisture clear MC={mc}%", {"moisture": m})


class ConnectionsAgent:
    name = "connections"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("connections") or {}
        if not c.get("hardware_kits_matched"):
            return GateResult(self.name, "HOLD", "Hardware kits not matched to piece marks", {"connections": c})
        incomplete = list(c.get("incomplete_patterns") or [])
        if incomplete:
            return GateResult(self.name, "HOLD", "Incomplete patterns: " + ", ".join(incomplete), {"connections": c})
        if c.get("structural_failure"):
            return GateResult(self.name, "FAIL", "Structural connection failure reported", {"connections": c})
        return GateResult(self.name, "PASS", "Connections clear", {"connections": c})


class TempBracingAgent:
    name = "temp-bracing"

    def plan(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bracing") or {}
        miss = _missing_flags(b, ("plan_issued", "shear_wall_brace_plan"))
        if miss:
            return GateResult(self.name, "HOLD", "Bracing plan incomplete: " + ", ".join(miss), {"bracing": b})
        return GateResult(self.name, "PASS", "Temporary bracing plan issued", {"bracing": b})

    def lock_in(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bracing") or {}
        if b.get("unstable_without_brace"):
            return GateResult(self.name, "FAIL", "Unstable members without required braces", {"bracing": b})
        if not b.get("braces_installed"):
            return GateResult(self.name, "HOLD", "Required braces not installed", {"bracing": b})
        if not b.get("diaphragm_locked"):
            return GateResult(self.name, "HOLD", "Early diaphragm not locked in", {"bracing": b})
        return GateResult(self.name, "PASS", "Bracing + diaphragm locked", {"bracing": b})


class PanelErectAgent:
    name = "panel-erect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("panels") or {}
        if not p.get("sequence"):
            return GateResult(self.name, "HOLD", "Panel sequence missing", {"panels": p})
        if p.get("force_fit"):
            return GateResult(self.name, "HOLD", "Force-fit attempted — stop and re-survey", {"panels": p})
        if p.get("field_cut_unapproved"):
            return GateResult(self.name, "HOLD", "Unapproved field cut/opening", {"panels": p})
        if not p.get("seated"):
            return GateResult(self.name, "HOLD", "Panels not seated per erection drawing", {"panels": p})
        return GateResult(self.name, "PASS", f"Panels seated sequence={len(p.get('sequence') or [])}", {"panels": p})


class GlulamFrameAgent:
    name = "glulam-frame"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("glulam") or {}
        if not g and not ctx.get("require_glulam"):
            return GateResult(self.name, "SKIP", "No glulam scope this pick", {})
        miss = _missing_flags(g, ("camber_orientation_ok", "base_hardware_ready", "seats_ready"))
        if miss:
            return GateResult(self.name, "HOLD", "Glulam incomplete: " + ", ".join(miss), {"glulam": g})
        return GateResult(self.name, "PASS", "Glulam frame clear", {"glulam": g})


class HybridInterfaceAgent:
    name = "hybrid-interface"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        h = ctx.get("hybrid") or {}
        if h.get("required") is False:
            return GateResult(self.name, "PASS", "No hybrid interface this zone", {"hybrid": h})
        miss = _missing_flags(h, ("podium_released", "steel_primed_or_na", "movement_details_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Hybrid interface incomplete: " + ", ".join(miss), {"hybrid": h})
        return GateResult(self.name, "PASS", "Hybrid interface released", {"hybrid": h})


class WeatherGateAgent:
    name = "weather-gate"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        wind = _num(w.get("wind_kph"), 0) or 0
        limit = _num(w.get("wind_hold_kph"), DEFAULT_WIND_HOLD_KPH) or DEFAULT_WIND_HOLD_KPH
        holds: list[str] = []
        if wind >= limit:
            holds.append(f"wind {wind}kph ≥ {limit}kph")
        if w.get("active_precip") and not w.get("protection_effective"):
            holds.append("active precip without effective protection")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", f"Weather CLEAR wind={wind}kph", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("bracing", {}).get("unstable_without_brace"):
            violations.append("unstable member without brace")
        if ctx.get("connections", {}).get("structural_failure"):
            violations.append("structural connection failure")
        if ctx.get("crane", {}).get("overload"):
            violations.append("crane overload")
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


class AssemblySystemsAgent:
    name = "assembly-systems"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("assembly") or {}
        issues = _missing_flags(a, ("fire_sequencing_ok", "mep_openings_coordinated"))
        if a.get("topping_requested") and not a.get("acoustic_stack_ready"):
            issues.append("acoustic stack not ready")
        if issues:
            return GateResult(self.name, "HOLD", "; ".join(issues), {"assembly": a})
        return GateResult(self.name, "PASS", "Fire/acoustic/MEP sequencing clear", {"assembly": a})


class FinishProtectAgent:
    name = "finish-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("finish") or {}
        if f.get("exposed_architecture") and not f.get("protection_plan"):
            return GateResult(self.name, "HOLD", "Exposed finish protection plan missing", {"finish": f})
        if f.get("padded_rigging") is False:
            return GateResult(self.name, "HOLD", "Padded/non-marring rigging not confirmed", {"finish": f})
        return GateResult(self.name, "PASS", "Finish protection clear", {"finish": f})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        checks = [c for c in (q.get("checks") or []) if c.get("phase", "pre") == phase]
        if not checks:
            # synthesize from flags
            if phase == "pre" and q.get("pre_hold_points_clear"):
                return GateResult(self.name, "PASS", "Pre-erect QA hold points clear", {})
            if phase != "pre" and q.get("pick_hold_points_clear"):
                return GateResult(self.name, "PASS", f"{phase} QA clear", {})
            return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})
        failed = [c for c in checks if not c.get("passed")]
        if failed:
            return GateResult(
                self.name,
                "FAIL",
                "QA failed: " + "; ".join(c.get("description", "check") for c in failed),
                {"failed": failed},
            )
        return GateResult(self.name, "PASS", f"QA {len(checks)} checks passed", {})


class ErectLeadAgent:
    name = "erect-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked erection"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('erect_id', ctx.get('level', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(
            self.name,
            status,
            f"{detail} [{hint}]",
            {"decision_hint": hint, "workflow": workflow, "level": ctx.get("level")},
        )
