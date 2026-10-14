"""Deterministic specialist gates for SOE / shoring."""

from __future__ import annotations

from typing import Any

from modules.soe_swarm.schemas import GateResult

ERECT_ROLES = ('soe_lead', 'pile_op', 'excavator_op', 'welder_fitter', 'anchor_crew', 'qc_tech', 'safety_watch')


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class DesignSubmittalAgent:
    name = "design-submittal"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("design") or {}
        miss = _missing(d, ("pe_stamped_approved", "products_approved", "monitoring_plan_approved"))
        if miss:
            return GateResult(self.name, "HOLD", "SOE design/submittals incomplete: " + ", ".join(miss), {"design": d})
        return GateResult(self.name, "PASS", "PE SOE design/submittals clear", {"design": d})


class SurveyMonitoringAgent:
    name = "survey-monitoring"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("monitoring") or {}
        if not m.get("baseline_set"):
            return GateResult(self.name, "HOLD", "Monitoring baseline not established", {"monitoring": m})
        if m.get("readings_current") is False:
            return GateResult(self.name, "HOLD", "Required monitoring readings overdue", {"monitoring": m})
        if m.get("alarm_exceeded"):
            return GateResult(self.name, "FAIL", "Monitoring alarm exceeded — stop excavate / eng review", {"monitoring": m})
        if m.get("alert_exceeded"):
            return GateResult(self.name, "HOLD", "Monitoring alert exceeded — eng review before deeper dig", {"monitoring": m})
        return GateResult(self.name, "PASS", "Survey/monitoring clear", {"monitoring": m})


class SoldierPilesAgent:
    name = "soldier-piles"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("soldier_piles") or {}
        if p.get("required") is False:
            return GateResult(self.name, "SKIP", "No soldier piles this gate", {})
        if p.get("tip_ok") is False:
            return GateResult(self.name, "HOLD", "Soldier pile tip/embedment short", {"soldier_piles": p})
        if p.get("plumb_ok") is False:
            return GateResult(self.name, "HOLD", "Soldier pile plumb/location out of tolerance", {"soldier_piles": p})
        return GateResult(self.name, "PASS", "Soldier piles clear", {"soldier_piles": p})


class LaggingAgent:
    name = "lagging"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("lagging") or {}
        if l.get("required") is False:
            return GateResult(self.name, "SKIP", "No lagging scope", {})
        if l.get("exposed_face_over_limit"):
            return GateResult(self.name, "HOLD", "Exposed face without lagging beyond allowed height/time", {"lagging": l})
        if l.get("gaps_unpacked"):
            return GateResult(self.name, "HOLD", "Lagging gaps not packed/backfilled", {"lagging": l})
        if not l.get("installed_ok"):
            return GateResult(self.name, "HOLD", "Lagging not installed/accepted", {"lagging": l})
        return GateResult(self.name, "PASS", "Lagging clear", {"lagging": l})


class SheetPileAgent:
    name = "sheet-pile"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("sheet_pile") or {}
        if s.get("required") is False:
            return GateResult(self.name, "SKIP", "No sheet pile this gate", {})
        if s.get("interlock_broken"):
            return GateResult(self.name, "HOLD", "Sheet interlocks broken/lost", {"sheet_pile": s})
        if s.get("tip_ok") is False and not s.get("eng_direction"):
            return GateResult(self.name, "HOLD", "Sheet tip short without eng direction", {"sheet_pile": s})
        return GateResult(self.name, "PASS", "Sheet pile clear", {"sheet_pile": s})


class WalesStrutsAgent:
    name = "wales-struts"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("bracing") or {}
        if w.get("required") is False:
            return GateResult(self.name, "SKIP", "No internal bracing this gate", {})
        if w.get("missing_for_stage"):
            return GateResult(self.name, "FAIL", "Required wale/strut missing for current/next stage", {"bracing": w})
        if w.get("connections_ok") is False:
            return GateResult(self.name, "HOLD", "Brace connections/pins incomplete", {"bracing": w})
        if w.get("preload_ok") is False:
            return GateResult(self.name, "HOLD", "Required preload/camber not applied", {"bracing": w})
        return GateResult(self.name, "PASS", "Wales/struts clear", {"bracing": w})


class TiebacksAnchorsAgent:
    name = "tiebacks-anchors"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("tiebacks") or {}
        if t.get("required") is False:
            return GateResult(self.name, "SKIP", "No tiebacks this gate", {})
        if t.get("required_for_stage") and not t.get("locked_off"):
            return GateResult(self.name, "HOLD", "Stage tiebacks not locked off", {"tiebacks": t})
        if t.get("proof_test_pass") is False:
            return GateResult(self.name, "HOLD", "Tieback proof/performance test failed", {"tiebacks": t})
        if t.get("grout_records_ok") is False:
            return GateResult(self.name, "HOLD", "Anchor grout records incomplete", {"tiebacks": t})
        return GateResult(self.name, "PASS", "Tiebacks/anchors clear", {"tiebacks": t})


class ExcavationStagesAgent:
    name = "excavation-stages"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("excavation") or {}
        depth = _num(e.get("current_depth_ft"))
        allowed = _num(e.get("allowed_depth_ft"))
        if depth is not None and allowed is not None and depth > allowed + 1e-6:
            return GateResult(self.name, "FAIL", f"Over-excavated {depth}ft > allowed {allowed}ft stage", {"excavation": e})
        if e.get("prior_braces_incomplete"):
            return GateResult(self.name, "HOLD", "Prior stage braces/anchors incomplete before next cut", {"excavation": e})
        if e.get("spoil_at_crest"):
            return GateResult(self.name, "HOLD", "Spoil surcharge at crest — pull back", {"excavation": e})
        return GateResult(self.name, "PASS", "Excavation stage clear", {"excavation": e})


class DewateringAgent:
    name = "dewatering"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("dewatering") or {}
        if d.get("required") is False:
            return GateResult(self.name, "PASS", "Dewatering not required", {"dewatering": d})
        if d.get("system_running") is False:
            return GateResult(self.name, "HOLD", "Dewatering system offline when required", {"dewatering": d})
        if d.get("uncontrolled_inflow"):
            return GateResult(self.name, "HOLD", "Uncontrolled inflow eroding face/bottom", {"dewatering": d})
        if d.get("drawdown_ok") is False:
            return GateResult(self.name, "HOLD", "Drawdown targets not met", {"dewatering": d})
        return GateResult(self.name, "PASS", "Dewatering clear", {"dewatering": d})


class LoadMonitoringAgent:
    name = "load-monitoring"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("loads") or {}
        if l.get("required") is False:
            return GateResult(self.name, "PASS", "Load monitoring not required", {"loads": l})
        if not l.get("cells_active"):
            return GateResult(self.name, "HOLD", "Required load cells inactive/missing", {"loads": l})
        if l.get("overload"):
            return GateResult(self.name, "FAIL", "Strut/anchor overload alarm", {"loads": l})
        return GateResult(self.name, "PASS", "Load monitoring clear", {"loads": l})


class BraceReleaseAgent:
    name = "brace-release"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("release") or {}
        if b.get("required") is False:
            return GateResult(self.name, "SKIP", "No brace release this gate", {})
        if b.get("sequence_ok") is False:
            return GateResult(self.name, "FAIL", "Out-of-sequence brace release", {"release": b})
        if not b.get("permanent_structure_ready"):
            return GateResult(self.name, "HOLD", "Permanent structure not ready to take load", {"release": b})
        if not b.get("monitoring_during"):
            return GateResult(self.name, "HOLD", "Monitoring not active during/after release", {"release": b})
        return GateResult(self.name, "PASS", "Brace release sequence clear", {"release": b})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        holds = []
        if w.get("storm_flood_risk") and not w.get("sumps_protected"):
            holds.append("storm/flood risk without sump/face protection")
        if w.get("freeze_thaw") and not w.get("face_protected"):
            holds.append("freeze-thaw without face protection")
        if w.get("crest_surcharge"):
            holds.append("unplanned crest surcharge")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/protection CLEAR", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("monitoring") or {}).get("alarm_exceeded") and (ctx.get("excavation") or {}).get("continuing_after_alarm"):
            violations.append("monitoring alarm ignored — continued excavate")
        if (ctx.get("bracing") or {}).get("missing_for_stage"):
            violations.append("unsupported excavation — missing brace")
        if (ctx.get("edge") or {}).get("unprotected"):
            violations.append("unprotected excavation edge fall hazard")
        if (ctx.get("face") or {}).get("collapse_indicators"):
            violations.append("imminent collapse indicators on face/crest")
        if (ctx.get("utilities") or {}).get("utility_strike"):
            violations.append("utility strike during SOE install")
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
            return GateResult(self.name, "PASS", "Pre-SOE QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class SoeLeadAgent:
    name = "soe-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked SOE work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
