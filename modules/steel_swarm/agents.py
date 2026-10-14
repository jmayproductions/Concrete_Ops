"""Deterministic specialist gates for structural steel erection."""

from __future__ import annotations

from typing import Any

from modules.steel_swarm.schemas import GateResult

DEFAULT_WIND_HOLD_KPH = 45.0
ERECT_ROLES = ('erect_lead', 'crane_operator', 'rigger', 'connector', 'brace_crew', 'qc_tech', 'safety_watch')


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _missing_flags(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class FabMillAgent:
    name = "fab-mill"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("fab") or {}
        miss = _missing_flags(
            s,
            ("shops_approved", "erection_drawings_approved", "sequence_published", "mill_certs_matched"),
        )
        if miss:
            return GateResult(self.name, "HOLD", "Missing: " + ", ".join(miss), {"fab": s})
        truck = s.get("truck") or {}
        if truck:
            expected = set(truck.get("expected_piece_marks") or [])
            onboard = set(truck.get("onboard_piece_marks") or [])
            if expected and onboard != expected:
                return GateResult(
                    self.name,
                    "HOLD",
                    f"Piece marks mismatch expected={sorted(expected)} got={sorted(onboard)}",
                    {"truck": truck},
                )
            heats_ok = truck.get("heat_numbers_matched")
            if heats_ok is False:
                return GateResult(self.name, "HOLD", "Heat numbers do not match mill certs", {"truck": truck})
        if s.get("member_damage"):
            return GateResult(self.name, "HOLD", "Damaged/deformed members on delivery", {"fab": s})
        return GateResult(self.name, "PASS", "Fab/mill/piece marks ready", {"fab": s})


class SurveyAnchorsAgent:
    name = "survey-anchors"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("anchors") or {}
        if not a:
            return GateResult(self.name, "HOLD", "No anchor/baseplate survey package", {})
        if a.get("within_tolerance") is False:
            return GateResult(self.name, "FAIL", f"Anchors out of tolerance: {a.get('notes', 'see survey')}", {"anchors": a})
        miss = _missing_flags(a, ("layout_verified", "leveling_plates_set", "baseplate_elevation_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Anchor survey incomplete: " + ", ".join(miss), {"anchors": a})
        return GateResult(self.name, "PASS", "Anchors/baseplates within tolerance", {"anchors": a})


class CraneLogisticsAgent:
    name = "crane-logistics"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("crane") or {}
        miss = _missing_flags(c, ("chart_ok", "pick_plan_verified", "exclusion_zone_set"))
        if miss:
            return GateResult(self.name, "HOLD", "Crane logistics incomplete: " + ", ".join(miss), {"crane": c})
        if c.get("overload"):
            return GateResult(self.name, "FAIL", "Crane overload indicated", {"crane": c})
        return GateResult(self.name, "PASS", "Crane/logistics clear", {"crane": c})


class TempBracingAgent:
    name = "temp-bracing"

    def plan(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bracing") or {}
        if not b.get("plan_issued"):
            return GateResult(self.name, "HOLD", "Temporary bracing plan not issued", {"bracing": b})
        return GateResult(self.name, "PASS", "Temporary bracing plan issued", {"bracing": b})

    def lock_in(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bracing") or {}
        if b.get("unstable_without_brace"):
            return GateResult(self.name, "FAIL", "Unstable framing without required braces", {"bracing": b})
        if not b.get("braces_installed"):
            return GateResult(self.name, "HOLD", "Required temporary braces not installed", {"bracing": b})
        if not b.get("stability_locked"):
            return GateResult(self.name, "HOLD", "Stability not locked for advance", {"bracing": b})
        return GateResult(self.name, "PASS", "Bracing/stability locked", {"bracing": b})


class BoltingAgent:
    name = "bolting"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bolting") or {}
        if not b.get("kits_matched"):
            return GateResult(self.name, "HOLD", "Bolt kits not matched to joints", {"bolting": b})
        incomplete = list(b.get("incomplete_joints") or [])
        if incomplete:
            return GateResult(self.name, "HOLD", "Incomplete joints: " + ", ".join(incomplete), {"bolting": b})
        if b.get("pretension_required") and not b.get("tension_log_complete"):
            return GateResult(self.name, "HOLD", "Pretension/torque log incomplete", {"bolting": b})
        if b.get("structural_failure"):
            return GateResult(self.name, "FAIL", "Structural bolting failure reported", {"bolting": b})
        return GateResult(self.name, "PASS", "Bolting clear", {"bolting": b})


class WeldingAgent:
    name = "welding"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("welding") or {}
        if not w and not ctx.get("require_welding"):
            return GateResult(self.name, "SKIP", "No weld scope this gate", {})
        if w.get("required") is False:
            return GateResult(self.name, "PASS", "No field weld scope", {"welding": w})
        miss = _missing_flags(w, ("wps_available", "welders_qualified", "visual_accepted"))
        if miss:
            return GateResult(self.name, "HOLD", "Welding incomplete: " + ", ".join(miss), {"welding": w})
        if w.get("ndt_required") and not w.get("ndt_complete"):
            return GateResult(self.name, "HOLD", "Required NDT not complete", {"welding": w})
        if w.get("cracked_weld"):
            return GateResult(self.name, "FAIL", "Cracked weld reported — stop and repair per WPS", {"welding": w})
        return GateResult(self.name, "PASS", "Welding/NDT clear", {"welding": w})


class PlumbAlignmentAgent:
    name = "plumb-alignment"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("plumb") or {}
        if not p:
            return GateResult(self.name, "HOLD", "No plumb/alignment package", {})
        if p.get("within_tolerance") is False:
            return GateResult(self.name, "HOLD", f"Out of tolerance: {p.get('notes', 'see survey')}", {"plumb": p})
        if not p.get("columns_checked"):
            return GateResult(self.name, "HOLD", "Column plumb checks incomplete", {"plumb": p})
        return GateResult(self.name, "PASS", "Plumb/alignment within AISC/project tolerance", {"plumb": p})


class DeckingAgent:
    name = "decking"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("decking") or {}
        if not d and not ctx.get("require_decking"):
            return GateResult(self.name, "SKIP", "No decking scope", {})
        if d.get("required") is False:
            return GateResult(self.name, "PASS", "No decking this level", {"decking": d})
        if not d.get("framing_ready"):
            return GateResult(self.name, "HOLD", "Framing not ready for deck loads", {"decking": d})
        if not d.get("attachment_pattern_ok"):
            return GateResult(self.name, "HOLD", "Deck attachment pattern not confirmed", {"decking": d})
        return GateResult(self.name, "PASS", "Decking release clear", {"decking": d})


class FireproofingAgent:
    name = "fireproofing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("fireproofing") or {}
        if not f:
            return GateResult(self.name, "SKIP", "No fireproofing gate this workflow", {})
        if f.get("required") is False:
            return GateResult(self.name, "PASS", "No fireproofing this closeout", {"fireproofing": f})
        if not f.get("surface_prep_ok"):
            return GateResult(self.name, "HOLD", "Fireproofing surface prep not acceptable", {"fireproofing": f})
        if not f.get("sequencing_ok"):
            return GateResult(self.name, "HOLD", "Connections/decking sequencing blocks fireproofing", {"fireproofing": f})
        return GateResult(self.name, "PASS", "Fireproofing sequencing clear", {"fireproofing": f})


class CoatingsAgent:
    name = "coatings"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("coatings") or {}
        if not c:
            return GateResult(self.name, "SKIP", "No coatings scope", {})
        if c.get("damage") and not c.get("touchup_plan"):
            return GateResult(self.name, "HOLD", "Coating/galvanizing damage without touch-up plan", {"coatings": c})
        return GateResult(self.name, "PASS", "Coatings clear", {"coatings": c})


class GroutBaseplateAgent:
    name = "grout-baseplate"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("grout") or {}
        if g.get("required") is False:
            return GateResult(self.name, "PASS", "Grout not required this gate", {"grout": g})
        miss = _missing_flags(g, ("materials_approved", "alignment_accepted"))
        if miss:
            return GateResult(self.name, "HOLD", "Grout incomplete: " + ", ".join(miss), {"grout": g})
        return GateResult(self.name, "PASS", "Baseplate grout release clear", {"grout": g})


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
        if w.get("lightning"):
            holds.append("lightning / storm active")
        if w.get("active_precip") and w.get("weld_exposed") and not w.get("shelter"):
            holds.append("precip on exposed weld without shelter")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", f"Weather CLEAR wind={wind}kph", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("bracing", {}).get("unstable_without_brace"):
            violations.append("unstable framing without brace")
        if ctx.get("crane", {}).get("overload"):
            violations.append("crane overload")
        if ctx.get("bolting", {}).get("structural_failure"):
            violations.append("structural bolting failure")
        if ctx.get("welding", {}).get("cracked_weld"):
            violations.append("cracked critical weld")
        if violations:
            return GateResult(self.name, "FAIL", "STOP-WORK: " + "; ".join(violations), {"violations": violations})
        return GateResult(self.name, "PASS", "No fail-safe violations", {})


class CrewOpsAgent:
    name = "crew-ops"

    def evaluate(self, ctx: dict[str, Any], require_briefing: bool = True) -> GateResult:
        crew = ctx.get("crew") or {}
        roles = set(crew.get("roles") or [])
        required = list(ERECT_ROLES)
        if (ctx.get("welding") or {}).get("required"):
            if "welder" not in roles:
                required.append("welder")
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
        checks = [c for c in (q.get("checks") or []) if c.get("phase", "pre") == phase]
        if not checks:
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
