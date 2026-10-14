"""Deterministic specialist gates for heavy-lift / crane day."""

from __future__ import annotations

from typing import Any

from modules.heavy_lift_swarm.schemas import GateResult

ERECT_ROLES = ('lift_lead', 'crane_op', 'rigger', 'signal_person', 'spotter', 'qc_tech', 'safety_watch')


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class LiftPlanAgent:
    name = "lift-plan"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("plan") or {}
        if p.get("critical") and not p.get("approved"):
            return GateResult(self.name, "HOLD", "Critical lift plan not approved", {"plan": p})
        miss = _missing(p, ("weight_known", "radius_known", "roles_named"))
        if miss:
            return GateResult(self.name, "HOLD", "Lift plan incomplete: " + ", ".join(miss), {"plan": p})
        return GateResult(self.name, "PASS", "Lift plan clear", {"plan": p})


class CraneCertsAgent:
    name = "crane-certs"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("certs") or {}
        if c.get("crane_inspection_current") is False:
            return GateResult(self.name, "HOLD", "Crane inspection not current", {"certs": c})
        if c.get("operator_certified") is False:
            return GateResult(self.name, "HOLD", "Operator not certified for crane type", {"certs": c})
        if c.get("rigger_qualified") is False:
            return GateResult(self.name, "HOLD", "Rigger/signal not qualified", {"certs": c})
        return GateResult(self.name, "PASS", "Crane/crew certs clear", {"certs": c})


class GroundBearingAgent:
    name = "ground-bearing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("ground") or {}
        if g.get("outriggers_set") is False:
            return GateResult(self.name, "HOLD", "Outriggers not fully set per chart", {"ground": g})
        if g.get("mats_ok") is False:
            return GateResult(self.name, "HOLD", "Mats/cribbing inadequate for bearing", {"ground": g})
        if g.get("soft_ground"):
            return GateResult(self.name, "HOLD", "Soft/void ground unresolved", {"ground": g})
        return GateResult(self.name, "PASS", "Ground bearing/setup clear", {"ground": g})


class RiggingGearAgent:
    name = "rigging-gear"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        r = ctx.get("rigging") or {}
        if r.get("damaged"):
            return GateResult(self.name, "FAIL", "Damaged rigging in service", {"rigging": r})
        if r.get("capacity_ok") is False:
            return GateResult(self.name, "HOLD", "Rigging capacity/angle insufficient", {"rigging": r})
        if not r.get("inspected"):
            return GateResult(self.name, "HOLD", "Rigging not inspected this shift", {"rigging": r})
        return GateResult(self.name, "PASS", "Rigging gear clear", {"rigging": r})


class PickPathAgent:
    name = "pick-path"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("path") or {}
        if p.get("obstructed"):
            return GateResult(self.name, "HOLD", "Pick/swing path obstructed", {"path": p})
        if p.get("blind_uncontrolled"):
            return GateResult(self.name, "HOLD", "Blind pick without controls", {"path": p})
        return GateResult(self.name, "PASS", "Pick path clear", {"path": p})


class PowerLinesAgent:
    name = "power-lines"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("power_lines") or {}
        if p.get("encroachment"):
            return GateResult(self.name, "FAIL", "Power line encroachment without controls", {"power_lines": p})
        if p.get("present") and not p.get("clearance_ok") and not p.get("spotter_plan"):
            return GateResult(self.name, "HOLD", "Power line clearance/spotter plan incomplete", {"power_lines": p})
        return GateResult(self.name, "PASS", "Power line clearance clear", {"power_lines": p})


class ExclusionZoneAgent:
    name = "exclusion-zone"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("exclusion") or {}
        if e.get("under_load"):
            return GateResult(self.name, "FAIL", "Personnel under suspended load", {"exclusion": e})
        if e.get("breached"):
            return GateResult(self.name, "FAIL", "Exclusion zone breached", {"exclusion": e})
        if not e.get("marked"):
            return GateResult(self.name, "HOLD", "Exclusion zone not marked/enforced", {"exclusion": e})
        return GateResult(self.name, "PASS", "Exclusion zone clear", {"exclusion": e})


class SignalCommsAgent:
    name = "signal-comms"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("comms") or {}
        if s.get("lost_during_critical"):
            return GateResult(self.name, "FAIL", "Lost comms during critical lift", {"comms": s})
        if not s.get("signal_person") or not s.get("channel_confirmed"):
            return GateResult(self.name, "HOLD", "Signal person/comms not confirmed", {"comms": s})
        return GateResult(self.name, "PASS", "Signal/comms clear", {"comms": s})


class WeatherWindAgent:
    name = "weather-wind"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather/wind data", {})
        wind = _num(w.get("wind_mph"))
        limit = _num(w.get("wind_limit_mph"), 20.0) or 20.0
        if w.get("lightning"):
            return GateResult(self.name, "FAIL", "Lightning — stop lifting", {"weather": w})
        if wind is not None and wind > limit:
            return GateResult(self.name, "FAIL", f"Wind {wind} mph > limit {limit} mph", {"weather": w})
        if w.get("poor_visibility"):
            return GateResult(self.name, "HOLD", "Visibility too poor for signaling", {"weather": w})
        return GateResult(self.name, "PASS", "Weather/wind CLEAR", {"weather": w})


class LoadChartAgent:
    name = "load-chart"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("chart") or {}
        if l.get("unknown_weight") and l.get("critical"):
            return GateResult(self.name, "FAIL", "Unknown weight on critical lift", {"chart": l})
        if l.get("unknown_weight"):
            return GateResult(self.name, "HOLD", "Load weight unknown — verify before lift", {"chart": l})
        if l.get("within_chart") is False:
            return GateResult(self.name, "FAIL", "Load exceeds chart capacity at radius/config", {"chart": l})
        if l.get("config_match") is False:
            return GateResult(self.name, "HOLD", "Crane config does not match chart", {"chart": l})
        return GateResult(self.name, "PASS", "Load chart clear", {"chart": l})


class TagLineControlAgent:
    name = "tagline-control"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("taglines") or {}
        if t.get("required") is False:
            return GateResult(self.name, "SKIP", "Tag lines not required", {})
        if t.get("uncontrolled_spin"):
            return GateResult(self.name, "HOLD", "Uncontrolled load spin in congested area", {"taglines": t})
        if t.get("riding_load"):
            return GateResult(self.name, "FAIL", "Personnel riding the load", {"taglines": t})
        return GateResult(self.name, "PASS", "Tag-line control clear", {"taglines": t})


class TandemCriticalAgent:
    name = "tandem-critical"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("tandem") or {}
        if t.get("required") is False:
            return GateResult(self.name, "SKIP", "No tandem/critical extras", {})
        if not t.get("share_calculated"):
            return GateResult(self.name, "HOLD", "Tandem load share not calculated", {"tandem": t})
        if not t.get("single_signal"):
            return GateResult(self.name, "HOLD", "Single signal authority not established", {"tandem": t})
        if t.get("checklist_signed") is False:
            return GateResult(self.name, "HOLD", "Critical/tandem checklist not signed", {"tandem": t})
        return GateResult(self.name, "PASS", "Tandem/critical extras clear", {"tandem": t})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("exclusion") or {}).get("under_load") or (ctx.get("exclusion") or {}).get("breached"):
            violations.append("personnel under load / exclusion breached")
        if (ctx.get("power_lines") or {}).get("encroachment"):
            violations.append("power line encroachment")
        w = ctx.get("weather") or {}
        wind = _num(w.get("wind_mph"))
        limit = _num(w.get("wind_limit_mph"), 20.0) or 20.0
        if w.get("lightning") or (wind is not None and wind > limit):
            violations.append("wind/lightning lift limit exceeded")
        ch = ctx.get("chart") or {}
        if ch.get("within_chart") is False or (ch.get("unknown_weight") and ch.get("critical")):
            violations.append("overload or unknown critical weight")
        if (ctx.get("rigging") or {}).get("damaged"):
            violations.append("damaged rigging in use")
        if (ctx.get("comms") or {}).get("lost_during_critical"):
            violations.append("lost comms during critical lift")
        if (ctx.get("taglines") or {}).get("riding_load"):
            violations.append("riding the load")
        if violations:
            return GateResult(self.name, "FAIL", "STOP-WORK: " + "; ".join(dict.fromkeys(violations)), {"violations": list(dict.fromkeys(violations))})
        return GateResult(self.name, "PASS", "No fail-safe violations", {})


class CrewOpsAgent:
    name = "crew-ops"

    def evaluate(self, ctx: dict[str, Any], require_briefing: bool = True) -> GateResult:
        crew = ctx.get("crew") or {}
        roles = set(crew.get("roles") or [])
        missing = [r for r in ERECT_ROLES if r not in roles]
        if missing:
            return GateResult(self.name, "HOLD", "Missing roles: " + ", ".join(missing), {"missing": missing})
        if require_briefing and not crew.get("briefing_complete"):
            return GateResult(self.name, "HOLD", "Lift briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Lift crew ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-lift docs clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} lift docs clear", {})
        return GateResult(self.name, "HOLD", f"No lift QA evidence for phase={phase}", {"qa": q})


class LiftLeadAgent:
    name = "lift-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked lift"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Lift sequence ready for {ctx.get('zone_id', ctx.get('pick_id', 'pick'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
