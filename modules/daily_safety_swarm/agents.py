"""Deterministic specialist gates for daily safety."""

from __future__ import annotations

from typing import Any

from modules.daily_safety_swarm.schemas import GateResult

ERECT_ROLES = ('safety_lead', 'supervisor', 'fire_watch', 'cse_attendant', 'competent_person', 'first_aid', 'qc_tech')


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class DailyBriefingAgent:
    name = "daily-briefing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("briefing") or {}
        if not b.get("complete"):
            return GateResult(self.name, "HOLD", "Pre-shift briefing/JHA incomplete", {"briefing": b})
        if not b.get("high_risk_called_out") and b.get("has_high_risk"):
            return GateResult(self.name, "HOLD", "High-risk tasks not covered in briefing", {"briefing": b})
        return GateResult(self.name, "PASS", "Daily briefing clear", {"briefing": b})


class PpeReadinessAgent:
    name = "ppe-readiness"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("ppe") or {}
        if p.get("missing"):
            return GateResult(self.name, "HOLD", "Missing PPE: " + ", ".join(p["missing"]), {"ppe": p})
        if p.get("damaged_in_use"):
            return GateResult(self.name, "HOLD", "Damaged/expired PPE in use", {"ppe": p})
        return GateResult(self.name, "PASS", "PPE readiness clear", {"ppe": p})


class HotWorkPermitAgent:
    name = "hot-work-permit"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        h = ctx.get("hot_work") or {}
        if h.get("required") is False:
            return GateResult(self.name, "SKIP", "No hot work", {})
        if h.get("no_permit") or not h.get("permit_valid"):
            return GateResult(self.name, "FAIL", "Hot work without valid permit", {"hot_work": h})
        if h.get("combustibles_cleared") is False:
            return GateResult(self.name, "HOLD", "Combustibles not cleared/protected", {"hot_work": h})
        if not h.get("extinguisher_staged"):
            return GateResult(self.name, "HOLD", "Fire extinguisher not staged", {"hot_work": h})
        return GateResult(self.name, "PASS", "Hot work permit clear", {"hot_work": h})


class FireWatchAgent:
    name = "fire-watch"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("fire_watch") or {}
        if f.get("required") is False:
            return GateResult(self.name, "SKIP", "No fire watch required", {})
        if not f.get("present_during"):
            return GateResult(self.name, "FAIL", "Fire watch not present during hot work", {"fire_watch": f})
        if f.get("post_watch_complete") is False:
            return GateResult(self.name, "HOLD", "Post hot-work fire watch not complete", {"fire_watch": f})
        return GateResult(self.name, "PASS", "Fire watch clear", {"fire_watch": f})


class ConfinedSpaceAgent:
    name = "confined-space"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("cse") or {}
        if c.get("required") is False:
            return GateResult(self.name, "SKIP", "No confined space entry", {})
        if not c.get("permit_valid"):
            return GateResult(self.name, "FAIL", "CSE without valid entry permit", {"cse": c})
        if not c.get("attendant_present"):
            return GateResult(self.name, "FAIL", "CSE attendant not present", {"cse": c})
        if c.get("gas_clear") is False:
            return GateResult(self.name, "FAIL", "Atmosphere not clear / tests failed", {"cse": c})
        if not c.get("rescue_plan"):
            return GateResult(self.name, "HOLD", "Rescue plan not confirmed", {"cse": c})
        return GateResult(self.name, "PASS", "Confined space entry clear", {"cse": c})


class LotoEnergyAgent:
    name = "loto-energy"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("loto") or {}
        if l.get("required") is False:
            return GateResult(self.name, "SKIP", "No LOTO this gate", {})
        if not l.get("applied"):
            return GateResult(self.name, "FAIL", "LOTO not applied for energized work", {"loto": l})
        if l.get("zero_energy_verified") is False:
            return GateResult(self.name, "FAIL", "Zero-energy not verified", {"loto": l})
        return GateResult(self.name, "PASS", "LOTO clear", {"loto": l})


class FallProtectionAgent:
    name = "fall-protection"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("fall") or {}
        if f.get("required") is False:
            return GateResult(self.name, "SKIP", "No fall exposure", {})
        if f.get("unprotected"):
            return GateResult(self.name, "FAIL", "Unprotected work at height / open holes", {"fall": f})
        if f.get("harness_ok") is False or f.get("anchorage_ok") is False:
            return GateResult(self.name, "HOLD", "PFAS/anchorage deficient", {"fall": f})
        return GateResult(self.name, "PASS", "Fall protection clear", {"fall": f})


class ExcavationCompetentAgent:
    name = "excavation-competent"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("excavation") or {}
        if e.get("required") is False:
            return GateResult(self.name, "SKIP", "No excavation", {})
        if not e.get("competent_person"):
            return GateResult(self.name, "HOLD", "Excavation competent person not named", {"excavation": e})
        if e.get("unprotected_trench"):
            return GateResult(self.name, "FAIL", "Unprotected trench/excavation", {"excavation": e})
        return GateResult(self.name, "PASS", "Excavation safety clear", {"excavation": e})


class CraneExclusionAgent:
    name = "crane-exclusion"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("crane") or {}
        if c.get("required") is False:
            return GateResult(self.name, "SKIP", "No crane/lift", {})
        if c.get("under_load"):
            return GateResult(self.name, "FAIL", "Personnel under suspended load / exclusion breached", {"crane": c})
        if not c.get("exclusion_marked") or not c.get("signal_person"):
            return GateResult(self.name, "HOLD", "Exclusion zone/signal person incomplete", {"crane": c})
        return GateResult(self.name, "PASS", "Crane exclusion clear", {"crane": c})


class IncidentStopAgent:
    name = "incident-stop"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        i = ctx.get("incident") or {}
        if i.get("stop_work") or i.get("serious_incident"):
            if i.get("continuing"):
                return GateResult(self.name, "FAIL", "Work continuing after stop-work/incident", {"incident": i})
            return GateResult(self.name, "FAIL", "Stop-work / incident — secure scene", {"incident": i})
        return GateResult(self.name, "PASS", "No active incident/stop-work", {"incident": i})


class WeatherEmergencyAgent:
    name = "weather-emergency"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if w.get("site_evacuate"):
            return GateResult(self.name, "FAIL", "Site emergency — evacuate", {"weather": w})
        holds = []
        if w.get("lightning") or w.get("high_wind"):
            holds.append("lightning/high wind — exposed/crane hold")
        if w.get("extreme_temp") and not w.get("controls"):
            holds.append("extreme temperature without controls")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/emergency CLEAR", {"weather": w})


class SubstanceFatigueAgent:
    name = "substance-fatigue"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("impairment") or {}
        if s.get("observed_impairment"):
            return GateResult(self.name, "HOLD", "Observed impairment — remove from safety-sensitive work", {"impairment": s})
        if s.get("fatigue_risk"):
            return GateResult(self.name, "HOLD", "Fatigue risk flagged for safety-sensitive tasks", {"impairment": s})
        return GateResult(self.name, "PASS", "No impairment/fatigue flags", {"impairment": s})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        hw = ctx.get("hot_work") or {}
        if hw.get("required") is not False and (hw.get("no_permit") or hw.get("permit_valid") is False):
            violations.append("hot work without permit")
        if (ctx.get("fire_watch") or {}).get("required") is not False and (ctx.get("fire_watch") or {}).get("present_during") is False and hw.get("active"):
            violations.append("fire watch missing during hot work")
        cse = ctx.get("cse") or {}
        if cse.get("required") and (not cse.get("permit_valid") or not cse.get("attendant_present") or cse.get("gas_clear") is False):
            violations.append("unsafe confined space entry")
        if (ctx.get("fall") or {}).get("unprotected"):
            violations.append("unprotected fall exposure")
        if (ctx.get("loto") or {}).get("required") and not (ctx.get("loto") or {}).get("applied"):
            violations.append("energized work without LOTO")
        if (ctx.get("incident") or {}).get("stop_work") and (ctx.get("incident") or {}).get("continuing"):
            violations.append("continuing after stop-work")
        if (ctx.get("crane") or {}).get("under_load"):
            violations.append("personnel under suspended load")
        if (ctx.get("excavation") or {}).get("unprotected_trench"):
            violations.append("unprotected trench")
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
            return GateResult(self.name, "HOLD", "Crew briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Safety staffing ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-shift safety docs clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} permit docs clear", {})
        return GateResult(self.name, "HOLD", f"No safety QA evidence for phase={phase}", {"qa": q})


class SafetyLeadAgent:
    name = "safety-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked unsafe work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Safety sequence ready for {ctx.get('zone_id', ctx.get('task', 'task'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
