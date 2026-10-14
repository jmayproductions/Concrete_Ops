"""Deterministic specialist gates for special inspections."""

from __future__ import annotations

from typing import Any

from modules.special_inspections_swarm.schemas import GateResult

ERECT_ROLES = ('si_lead', 'gc_coordinator', 'soils_inspector', 'concrete_inspector', 'steel_inspector', 'document_ctrl', 'safety_watch')


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class StatementOfSiAgent:
    name = "statement-of-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("sossi") or {}
        if not s.get("approved"):
            return GateResult(self.name, "HOLD", "SOSSI not approved", {"sossi": s})
        if not s.get("frequency_matrix"):
            return GateResult(self.name, "HOLD", "SOSSI frequency matrix missing", {"sossi": s})
        return GateResult(self.name, "PASS", "SOSSI clear", {"sossi": s})


class ItpSchedulerAgent:
    name = "itp-scheduler"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        i = ctx.get("schedule") or {}
        if i.get("hold_points_staffed") is False:
            return GateResult(self.name, "HOLD", "Hold points not staffed: " + ", ".join(i.get("unstaffed") or ["unspecified"]), {"schedule": i})
        if i.get("notice_ok") is False:
            return GateResult(self.name, "HOLD", "SI notice lead time not met", {"schedule": i})
        return GateResult(self.name, "PASS", "SI schedule/dispatch clear", {"schedule": i})


class SoilsFoundationSiAgent:
    name = "soils-foundation-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("soils_si") or {}
        if s.get("required") is False:
            return GateResult(self.name, "SKIP", "No soils SI this gate", {})
        if not s.get("inspector_present") and s.get("required"):
            return GateResult(self.name, "HOLD", "Soils SI not present for hold point", {"soils_si": s})
        if s.get("accepted") is False:
            return GateResult(self.name, "HOLD", "Soils/foundation SI not accepted", {"soils_si": s})
        return GateResult(self.name, "PASS", "Soils/foundation SI clear", {"soils_si": s})


class ConcreteSiAgent:
    name = "concrete-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("concrete_si") or {}
        if c.get("required") is False:
            return GateResult(self.name, "SKIP", "No concrete SI this gate", {})
        if not c.get("inspector_present"):
            return GateResult(self.name, "HOLD", "Concrete SI not present for pour/rebar hold", {"concrete_si": c})
        if c.get("rebar_signed") is False:
            return GateResult(self.name, "HOLD", "Rebar/PT SI sign-off missing before pour", {"concrete_si": c})
        return GateResult(self.name, "PASS", "Concrete SI clear", {"concrete_si": c})


class SteelSiAgent:
    name = "steel-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("steel_si") or {}
        if s.get("required") is False:
            return GateResult(self.name, "SKIP", "No steel SI this gate", {})
        if not s.get("inspector_present"):
            return GateResult(self.name, "HOLD", "Steel SI not present", {"steel_si": s})
        if s.get("bolting_welding_ok") is False:
            return GateResult(self.name, "HOLD", "Bolting/welding SI incomplete", {"steel_si": s})
        return GateResult(self.name, "PASS", "Steel SI clear", {"steel_si": s})


class MasonrySiAgent:
    name = "masonry-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("masonry_si") or {}
        if m.get("required") is False:
            return GateResult(self.name, "SKIP", "No masonry SI this gate", {})
        if not m.get("inspector_present"):
            return GateResult(self.name, "HOLD", "Masonry SI not present", {"masonry_si": m})
        if m.get("pregrout_signed") is False:
            return GateResult(self.name, "HOLD", "Pre-grout SI sign-off missing", {"masonry_si": m})
        return GateResult(self.name, "PASS", "Masonry SI clear", {"masonry_si": m})


class WoodSiAgent:
    name = "wood-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("wood_si") or {}
        if w.get("required") is False:
            return GateResult(self.name, "SKIP", "No wood SI this gate", {})
        if not w.get("inspector_present"):
            return GateResult(self.name, "HOLD", "Wood/mass-timber SI not present", {"wood_si": w})
        return GateResult(self.name, "PASS", "Wood SI clear", {"wood_si": w})


class FireResistanceSiAgent:
    name = "fire-resistance-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("fire_si") or {}
        if f.get("required") is False:
            return GateResult(self.name, "SKIP", "No fire-resistance SI this gate", {})
        if not f.get("inspector_present"):
            return GateResult(self.name, "HOLD", "Fire-resistance SI not present", {"fire_si": f})
        if f.get("thickness_ok") is False:
            return GateResult(self.name, "HOLD", "SFRM/firestop SI thickness/continuity fail", {"fire_si": f})
        return GateResult(self.name, "PASS", "Fire-resistance SI clear", {"fire_si": f})


class NdtTestingAgent:
    name = "ndt-testing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        n = ctx.get("ndt") or {}
        if n.get("required") is False:
            return GateResult(self.name, "PASS", "NDT not required", {"ndt": n})
        if not n.get("complete"):
            return GateResult(self.name, "HOLD", "Required NDT incomplete", {"ndt": n})
        if n.get("open_indications"):
            return GateResult(self.name, "HOLD", "Open NDT indications: " + ", ".join(n["open_indications"]), {"ndt": n})
        return GateResult(self.name, "PASS", "NDT clear", {"ndt": n})


class AgencyCredentialsAgent:
    name = "agency-credentials"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("agency") or {}
        if a.get("approved") is False:
            return GateResult(self.name, "FAIL", "SI agency not approved by AHJ/owner", {"agency": a})
        if a.get("certs_current") is False:
            return GateResult(self.name, "HOLD", "Inspector certifications expired/missing for work type", {"agency": a})
        return GateResult(self.name, "PASS", "SI agency credentials clear", {"agency": a})


class HoldPointReleaseAgent:
    name = "hold-point-release"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        h = ctx.get("release") or {}
        if h.get("covering_without_si"):
            return GateResult(self.name, "FAIL", "Covering/concealing work without SI release", {"release": h})
        if not h.get("signed"):
            return GateResult(self.name, "HOLD", "Hold-point release not signed", {"release": h})
        if h.get("open_critical_ncrs"):
            return GateResult(self.name, "HOLD", "Critical NCRs open: " + ", ".join(h["open_critical_ncrs"]), {"release": h})
        return GateResult(self.name, "PASS", "Hold-point release clear", {"release": h})


class NonconformanceAgent:
    name = "nonconformance"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        n = ctx.get("ncr") or {}
        if n.get("required") is False and not n.get("open"):
            return GateResult(self.name, "PASS", "No open SI NCRs", {"ncr": n})
        if n.get("open"):
            critical = [x for x in n["open"] if x.get("critical")]
            if critical and not n.get("dispositioned"):
                return GateResult(self.name, "HOLD", "Critical SI NCRs not dispositioned", {"ncr": n})
            if n.get("rework_verified") is False:
                return GateResult(self.name, "HOLD", "SI NCR rework not verified", {"ncr": n})
        return GateResult(self.name, "PASS", "SI NCR status clear", {"ncr": n})


class FinalReportAgent:
    name = "final-report"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("final") or {}
        if not f.get("compiled"):
            return GateResult(self.name, "HOLD", "SI daily reports not compiled", {"final": f})
        if not f.get("agency_signed"):
            return GateResult(self.name, "HOLD", "Final SI report not signed by agency", {"final": f})
        if f.get("outstanding"):
            return GateResult(self.name, "HOLD", "Outstanding SI items: " + ", ".join(f["outstanding"]), {"final": f})
        return GateResult(self.name, "PASS", "Final SI report clear", {"final": f})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("release") or {}).get("covering_without_si"):
            violations.append("cover before required SI")
        if (ctx.get("agency") or {}).get("approved") is False:
            violations.append("unapproved SI agency on hold point")
        if (ctx.get("schedule") or {}).get("critical_skipped"):
            violations.append("critical structural hold point skipped")
        if (ctx.get("access") or {}).get("denied_unsafe"):
            violations.append("unsafe/denied access for required SI")
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
        if require_briefing and not crew.get("briefing_complete"):
            return GateResult(self.name, "HOLD", "SI coordination briefing incomplete", {})
        return GateResult(self.name, "PASS", f"SI staffing ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-SI program QA clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} SI docs clear", {})
        return GateResult(self.name, "HOLD", f"No SI QA evidence for phase={phase}", {"qa": q})


class SiLeadAgent:
    name = "si-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked SI / cover path"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"SI sequence ready for {ctx.get('zone_id', ctx.get('hold_point', 'hold'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
