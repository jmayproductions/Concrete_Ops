"""Deterministic specialist gates for survey / layout / control."""

from __future__ import annotations

from typing import Any

from modules.survey_swarm.schemas import GateResult

ERECT_ROLES = ('survey_lead', 'instrument_op', 'rod_person', 'cad_tech', 'qc_tech', 'safety_watch', 'gc_coordinator')


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class ControlNetworkAgent:
    name = "control-network"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("control") or {}
        if c.get("destroyed") and not c.get("reestablished"):
            return GateResult(self.name, "FAIL", "Primary control destroyed — re-establish before work", {"control": c})
        if not c.get("verified"):
            return GateResult(self.name, "HOLD", "Control network not verified", {"control": c})
        if c.get("closure_ok") is False:
            return GateResult(self.name, "HOLD", "Traverse/network closure out of tolerance", {"control": c})
        return GateResult(self.name, "PASS", "Control network clear", {"control": c})


class BenchmarksAgent:
    name = "benchmarks"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("benchmarks") or {}
        if not b.get("datum_tied"):
            return GateResult(self.name, "HOLD", "Benchmarks not tied to project datum", {"benchmarks": b})
        if b.get("disturbed"):
            return GateResult(self.name, "HOLD", "Benchmarks disturbed/heaved — re-verify", {"benchmarks": b})
        return GateResult(self.name, "PASS", "Benchmarks clear", {"benchmarks": b})


class StakeoutAgent:
    name = "stakeout"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("stakeout") or {}
        if not s.get("from_approved_rev"):
            return GateResult(self.name, "HOLD", "Stake-out not from approved revision/model", {"stakeout": s})
        if s.get("stakes_missing"):
            return GateResult(self.name, "HOLD", "Missing/disturbed stakes: " + ", ".join(s["stakes_missing"]), {"stakeout": s})
        if not s.get("cut_sheets_issued"):
            return GateResult(self.name, "HOLD", "Cut sheets not issued to trades", {"stakeout": s})
        return GateResult(self.name, "PASS", "Stake-out clear", {"stakeout": s})


class AsBuiltAgent:
    name = "as-built"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("asbuilt") or {}
        if a.get("required") is False:
            return GateResult(self.name, "PASS", "As-built not required this gate", {"asbuilt": a})
        if not a.get("captured"):
            return GateResult(self.name, "HOLD", "Required as-builts not captured before cover", {"asbuilt": a})
        if a.get("format_ok") is False:
            return GateResult(self.name, "HOLD", "As-built deliverable format incomplete", {"asbuilt": a})
        return GateResult(self.name, "PASS", "As-built capture clear", {"asbuilt": a})


class ToleranceCheckAgent:
    name = "tolerance-check"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("tolerance") or {}
        if t.get("within_tolerance") is False:
            return GateResult(self.name, "HOLD", f"Out of tolerance: {t.get('notes', 'see field book')}", {"tolerance": t})
        if not t.get("checked"):
            return GateResult(self.name, "HOLD", "Tolerance checks not recorded", {"tolerance": t})
        return GateResult(self.name, "PASS", "Tolerance checks clear", {"tolerance": t})


class BimLayoutAgent:
    name = "bim-layout"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bim") or {}
        if b.get("required") is False:
            return GateResult(self.name, "SKIP", "No BIM layout this gate", {})
        if b.get("superseded_model"):
            return GateResult(self.name, "HOLD", "Layout from superseded model revision", {"bim": b})
        if not b.get("revision_locked"):
            return GateResult(self.name, "HOLD", "Model revision not locked for layout", {"bim": b})
        return GateResult(self.name, "PASS", "BIM layout clear", {"bim": b})


class EmbedsAnchorLayoutAgent:
    name = "embeds-anchor-layout"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("embeds") or {}
        if e.get("required") is False:
            return GateResult(self.name, "SKIP", "No embeds layout this gate", {})
        if e.get("missing"):
            return GateResult(self.name, "HOLD", "Embeds/anchors not laid out: " + ", ".join(e["missing"]), {"embeds": e})
        if e.get("conflicts"):
            return GateResult(self.name, "HOLD", "Embed conflicts: " + ", ".join(e["conflicts"]), {"embeds": e})
        return GateResult(self.name, "PASS", "Embeds/anchor layout clear", {"embeds": e})


class GradeCheckingAgent:
    name = "grade-checking"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("grade") or {}
        if g.get("verified") is False:
            return GateResult(self.name, "HOLD", "Grade not verified vs design", {"grade": g})
        if g.get("reverse_slope"):
            return GateResult(self.name, "HOLD", "Reverse drainage slope detected", {"grade": g})
        return GateResult(self.name, "PASS", "Grade checking clear", {"grade": g})


class MonitoringSettlementAgent:
    name = "monitoring-settlement"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("monitoring") or {}
        if m.get("required") is False:
            return GateResult(self.name, "SKIP", "No deformation monitoring", {})
        if not m.get("baseline_set"):
            return GateResult(self.name, "HOLD", "Monitoring baseline not set", {"monitoring": m})
        if m.get("readings_current") is False:
            return GateResult(self.name, "HOLD", "Monitoring readings overdue", {"monitoring": m})
        if m.get("alarm"):
            return GateResult(self.name, "HOLD", "Monitoring alarm — eng review", {"monitoring": m})
        return GateResult(self.name, "PASS", "Settlement monitoring clear", {"monitoring": m})


class EquipmentCalibrationAgent:
    name = "equipment-calibration"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("equipment") or {}
        if e.get("calibration_current") is False:
            return GateResult(self.name, "HOLD", "Instrument calibration overdue", {"equipment": e})
        if e.get("field_check_ok") is False:
            return GateResult(self.name, "HOLD", "Field collimation/calibration check failed", {"equipment": e})
        return GateResult(self.name, "PASS", "Equipment calibration clear", {"equipment": e})


class UtilityLocateCoordAgent:
    name = "utility-locate-coord"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        u = ctx.get("utilities") or {}
        if u.get("required") is False:
            return GateResult(self.name, "PASS", "No dig/utility coordination this gate", {"utilities": u})
        if u.get("dig_without_locate"):
            return GateResult(self.name, "FAIL", "Stake/dig path without utility locate", {"utilities": u})
        if not u.get("ticket_known"):
            return GateResult(self.name, "HOLD", "Dig ticket status unknown for stake area", {"utilities": u})
        return GateResult(self.name, "PASS", "Utility locate coordination clear", {"utilities": u})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather/visibility data", {})
        holds = []
        if w.get("poor_visibility"):
            holds.append("fog/rain/shimmer — observations unreliable")
        if w.get("high_wind_critical"):
            holds.append("high wind affecting critical observations")
        if w.get("lightning"):
            holds.append("lightning — outdoor instrument hold")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/visibility CLEAR", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("edge") or {}).get("unprotected"):
            violations.append("surveying at unprotected open edge")
        if (ctx.get("control") or {}).get("destroyed") and not (ctx.get("control") or {}).get("reestablished"):
            violations.append("primary control destroyed — work continuing")
        if (ctx.get("traffic") or {}).get("uncontrolled"):
            violations.append("layout crew in live traffic without controls")
        if (ctx.get("utilities") or {}).get("dig_without_locate"):
            violations.append("dig/stake across unmarked utilities")
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
        return GateResult(self.name, "PASS", f"Party ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-survey QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} survey docs clear", {})
        return GateResult(self.name, "HOLD", f"No survey QA evidence for phase={phase}", {"qa": q})


class SurveyLeadAgent:
    name = "survey-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked survey/layout work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
