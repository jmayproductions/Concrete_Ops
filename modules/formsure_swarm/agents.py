"""Deterministic specialist gates for FormSure formwork."""

from __future__ import annotations

from typing import Any

from modules.formsure_swarm.schemas import GateResult

ERECT_ROLES = ('form_lead', 'carpenter_foreman', 'form_setter', 'pour_boss', 'shore_tech', 'qc_tech', 'safety_watch')


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class FormSystemAgent:
    name = "form-system"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("form") or {}
        if not f.get("system_type"):
            return GateResult(self.name, "HOLD", "Form system type not documented", {"form": f})
        if f.get("design_approved") is False:
            return GateResult(self.name, "HOLD", "Form design / pour-rate limits not approved", {"form": f})
        return GateResult(self.name, "PASS", f"Form system clear ({f.get('system_type')})", {"form": f})


class PanelAlignmentAgent:
    name = "panel-alignment"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("alignment") or {}
        if a.get("plumb_ok") is False or a.get("level_ok") is False or a.get("square_ok") is False:
            return GateResult(self.name, "HOLD", "Form out of plumb/level/square", {"alignment": a})
        if not a.get("checked"):
            return GateResult(self.name, "HOLD", "Alignment not checked", {"alignment": a})
        return GateResult(self.name, "PASS", "Panel alignment clear", {"alignment": a})


class ReleaseAgentAgent:
    name = "release-agent"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        r = ctx.get("release") or {}
        if r.get("required") is False:
            return GateResult(self.name, "SKIP", "Release agent not required", {})
        if r.get("coverage_ok") is False:
            return GateResult(self.name, "HOLD", "Release agent missing or uneven", {"release": r})
        if not r.get("applied"):
            return GateResult(self.name, "HOLD", "Release agent not applied", {"release": r})
        return GateResult(self.name, "PASS", "Release agent clear", {"release": r})


class TieRodsAgent:
    name = "tie-rods"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("ties") or {}
        if t.get("loose_or_missing"):
            return GateResult(self.name, "FAIL", "Loose or missing form ties", {"ties": t})
        if t.get("tension_ok") is False:
            return GateResult(self.name, "HOLD", "Tie tension/torque not verified", {"ties": t})
        if not t.get("spacing_ok"):
            return GateResult(self.name, "HOLD", "Tie spacing not confirmed per design", {"ties": t})
        return GateResult(self.name, "PASS", "Tie rods clear", {"ties": t})


class BracingLateralAgent:
    name = "bracing-lateral"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bracing") or {}
        if b.get("incomplete"):
            return GateResult(self.name, "FAIL", "Lateral bracing incomplete/critical", {"bracing": b})
        if b.get("installed") is False:
            return GateResult(self.name, "HOLD", "Lateral braces not installed", {"bracing": b})
        if b.get("torque_ok") is False:
            return GateResult(self.name, "HOLD", "Brace bolt torque/deflection check failed", {"bracing": b})
        return GateResult(self.name, "PASS", "Lateral bracing clear", {"bracing": b})


class LeakSealAgent:
    name = "leak-seal"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("leak") or {}
        mix = (ctx.get("mix") or {}).get("type") or "normal"
        if mix == "scc" and l.get("seams_sealed") is False:
            return GateResult(self.name, "HOLD", "SCC seams not leak-checked/sealed", {"leak": l, "mix": mix})
        if l.get("bleedout_path"):
            return GateResult(self.name, "HOLD", "Uncontrolled bleedout path at bulkhead/seam", {"leak": l})
        return GateResult(self.name, "PASS", "Leak seals clear", {"leak": l})


class PourDropAgent:
    name = "pour-drop"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("drop") or {}
        mix = str((ctx.get("mix") or {}).get("type") or "normal").lower()
        height = _num(d.get("free_fall_m"))
        if height is None:
            return GateResult(self.name, "HOLD", "Drop height not measured", {"drop": d})
        if d.get("chute_or_tremie"):
            return GateResult(self.name, "PASS", "Chute/tremie controls free fall", {"drop": d})
        limit = 0.6 if mix == "scc" else 1.2
        if mix in ("shotcrete", "hpc") and not d.get("direct_method"):
            return GateResult(self.name, "FAIL", "HPC/shotcrete requires direct nozzle/pump method", {"drop": d, "mix": mix})
        if height > limit:
            return GateResult(self.name, "FAIL", f"Free fall {height} m > limit {limit} m for {mix}", {"drop": d, "limit_m": limit})
        return GateResult(self.name, "PASS", f"Drop height clear ({height} m ≤ {limit} m)", {"drop": d})


class FormPressureAgent:
    name = "form-pressure"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("pressure") or {}
        rate = _num(p.get("pour_rate_m_per_hr"))
        limit = _num(p.get("design_rate_m_per_hr"))
        if p.get("blowout_risk"):
            return GateResult(self.name, "FAIL", "Form blowout risk — stop pour", {"pressure": p})
        if rate is not None and limit is not None and rate > limit:
            return GateResult(self.name, "FAIL", f"Pour rate {rate} m/hr > design {limit} m/hr", {"pressure": p})
        if p.get("within_design") is False:
            return GateResult(self.name, "HOLD", "Pour rate/lift height outside design", {"pressure": p})
        return GateResult(self.name, "PASS", "Form pressure clear", {"pressure": p})


class ShoringPropsAgent:
    name = "shoring-props"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("shores") or {}
        if s.get("unstable"):
            return GateResult(self.name, "FAIL", "Unstable shores/props — stop work", {"shores": s})
        if s.get("plumb_locked") is False:
            return GateResult(self.name, "HOLD", "Props not plumb/locked", {"shores": s})
        if s.get("bearing_ok") is False:
            return GateResult(self.name, "HOLD", "Soft mudsill / inadequate bearing", {"shores": s})
        return GateResult(self.name, "PASS", "Shores/props clear", {"shores": s})


class StripTimingAgent:
    name = "strip-timing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("strip") or {}
        if t.get("required") is False:
            return GateResult(self.name, "SKIP", "Strip not requested", {})
        strength = _num(t.get("strength_pct"))
        min_pct = _num(t.get("min_strength_pct"), 70.0) or 70.0
        if not t.get("strength_proof"):
            return GateResult(self.name, "FAIL", "No cylinder/maturity proof for strip", {"strip": t})
        if strength is not None and strength < min_pct:
            return GateResult(self.name, "FAIL", f"Strength {strength}% < min {min_pct}% for strip", {"strip": t})
        if t.get("reshore_required") and not t.get("reshore_ready"):
            return GateResult(self.name, "HOLD", "Reshore required but not ready", {"strip": t})
        return GateResult(self.name, "PASS", "Strip timing clear", {"strip": t})


class LoadTransferAgent:
    name = "load-transfer"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("load_transfer") or {}
        if l.get("sagging"):
            return GateResult(self.name, "FAIL", "Sagging soffit on release — re-support", {"load_transfer": l})
        if l.get("deflection_ok") is False:
            return GateResult(self.name, "HOLD", "Excessive deflection on pull/release test", {"load_transfer": l})
        if l.get("reshore_missing"):
            return GateResult(self.name, "HOLD", "Reshores missing before soffit strip", {"load_transfer": l})
        return GateResult(self.name, "PASS", "Load transfer clear", {"load_transfer": l})


class PanelReuseAgent:
    name = "panel-reuse"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("panels") or {}
        if p.get("damaged"):
            return GateResult(self.name, "HOLD", "Damaged panels tagged — do not reuse for finish work", {"panels": p})
        return GateResult(self.name, "PASS", "Panel reuse condition clear", {"panels": p})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("pressure") or {}).get("blowout_risk"):
            violations.append("form blowout risk")
        if (ctx.get("ties") or {}).get("loose_or_missing") and (ctx.get("bracing") or {}).get("incomplete"):
            violations.append("critical ties and braces compromised")
        elif (ctx.get("ties") or {}).get("loose_or_missing"):
            violations.append("loose/missing form ties")
        elif (ctx.get("bracing") or {}).get("incomplete"):
            violations.append("incomplete lateral bracing")
        d = ctx.get("drop") or {}
        mix = str((ctx.get("mix") or {}).get("type") or "normal").lower()
        height = _num(d.get("free_fall_m"))
        limit = 0.6 if mix == "scc" else 1.2
        if height is not None and height > limit and not d.get("chute_or_tremie"):
            violations.append("free-fall drop limit exceeded")
        p = ctx.get("pressure") or {}
        rate = _num(p.get("pour_rate_m_per_hr"))
        plimit = _num(p.get("design_rate_m_per_hr"))
        if rate is not None and plimit is not None and rate > plimit:
            violations.append("pour rate exceeds form design")
        t = ctx.get("strip") or {}
        strength = _num(t.get("strength_pct"))
        min_pct = _num(t.get("min_strength_pct"), 70.0) or 70.0
        if t.get("required") is not False and t.get("strength_proof") is False:
            violations.append("premature strip without strength proof")
        if t.get("required") is not False and strength is not None and strength < min_pct and t.get("strength_proof"):
            violations.append("premature strip below min strength")
        if (ctx.get("shores") or {}).get("unstable"):
            violations.append("unstable shores with collapse risk")
        if (ctx.get("load_transfer") or {}).get("sagging"):
            violations.append("soffit sagging after release")
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
            return GateResult(self.name, "HOLD", "Form/pour briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Form crew ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-pour form docs clear", {})
        if phase == "strip" and q.get("strip_docs_clear"):
            return GateResult(self.name, "PASS", "Strip docs clear", {})
        if phase not in ("pre",) and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} form docs clear", {})
        return GateResult(self.name, "HOLD", f"No form QA evidence for phase={phase}", {"qa": q})


class FormLeadAgent:
    name = "form-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked formwork sequence"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Formwork sequence ready for {ctx.get('zone_id', ctx.get('element_id', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
