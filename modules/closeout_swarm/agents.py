"""Deterministic specialist gates for closeout / punch / turnover."""

from __future__ import annotations

from typing import Any

from modules.closeout_swarm.schemas import GateResult

ERECT_ROLES = ('closeout_lead', 'qa_lead', 'pm_rep', 'trade_rep', 'safety_watch')


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class RoomReadinessAgent:
    name = "room-readiness"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        r = ctx.get("rooms") or {}
        if r.get("walkable") is False:
            return GateResult(self.name, "HOLD", "Rooms not walkable for punch: " + ", ".join(r.get("blocked_rooms") or ["see list"]), {"rooms": r})
        miss = _missing(r, ("ceilings_complete", "systems_operating", "safe_access"))
        if miss:
            return GateResult(self.name, "HOLD", "Room readiness incomplete: " + ", ".join(miss), {"rooms": r})
        return GateResult(self.name, "PASS", "Room readiness clear", {"rooms": r})


class PunchlistAgent:
    name = "punchlist"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("punch") or {}
        if not p.get("walk_complete"):
            return GateResult(self.name, "HOLD", "Punch walk not complete for zone", {"punch": p})
        if p.get("items_without_owner"):
            return GateResult(self.name, "HOLD", "Punch items missing owners: " + ", ".join(p["items_without_owner"][:8]), {"punch": p})
        open_critical = list(p.get("open_critical") or [])
        if open_critical and ctx.get("require_critical_clear"):
            return GateResult(self.name, "HOLD", "Open critical punches: " + ", ".join(open_critical[:8]), {"punch": p})
        if not p.get("photos_logged"):
            return GateResult(self.name, "HOLD", "Punch photo log incomplete", {"punch": p})
        return GateResult(self.name, "PASS", "Punchlist process clear", {"punch": p})


class LifeSafetyAgent:
    name = "life-safety"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("life_safety") or {}
        miss = _missing(l, ("egress_clear", "exit_signs_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Life safety incomplete: " + ", ".join(miss), {"life_safety": l})
        if l.get("emergency_lighting_failed"):
            return GateResult(self.name, "FAIL", "Emergency lighting failed under backup power", {"life_safety": l})
        if l.get("egress_blocked"):
            return GateResult(self.name, "FAIL", "Egress path blocked", {"life_safety": l})
        return GateResult(self.name, "PASS", "Life safety clear", {"life_safety": l})


class DoorHardwareAgent:
    name = "door-hardware"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("doors") or {}
        if not d and not ctx.get("require_doors"):
            return GateResult(self.name, "SKIP", "No door scope", {})
        if d.get("schedule_mismatches"):
            return GateResult(self.name, "HOLD", "Door/hardware mismatches: " + ", ".join(d["schedule_mismatches"][:8]), {"doors": d})
        if d.get("missing_fire_labels"):
            return GateResult(self.name, "HOLD", "Missing fire door labels: " + ", ".join(d["missing_fire_labels"][:8]), {"doors": d})
        if not d.get("function_tested"):
            return GateResult(self.name, "HOLD", "Door function tests incomplete", {"doors": d})
        return GateResult(self.name, "PASS", "Door/hardware clear", {"doors": d})


class FinishesQaAgent:
    name = "finishes-qa"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("finishes") or {}
        if f.get("systemic_failures"):
            return GateResult(self.name, "HOLD", "Systemic finish failures without rework plan", {"finishes": f})
        if not f.get("walk_complete") and ctx.get("require_finishes"):
            return GateResult(self.name, "HOLD", "Finishes punch walk incomplete", {"finishes": f})
        return GateResult(self.name, "PASS", "Finishes QA clear", {"finishes": f})


class FireProtectionAgent:
    name = "fire-protection"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        fp = ctx.get("fire_protection") or {}
        if fp.get("required") is False:
            return GateResult(self.name, "PASS", "FP closeout not required this gate", {"fire_protection": fp})
        if not fp.get("tests_complete"):
            return GateResult(self.name, "HOLD", "Required fire protection tests incomplete", {"fire_protection": fp})
        if fp.get("tests_failed"):
            return GateResult(self.name, "FAIL", "Fire protection tests failed: " + ", ".join(fp["tests_failed"]), {"fire_protection": fp})
        return GateResult(self.name, "PASS", "Fire protection closeout clear", {"fire_protection": fp})


class CommissioningAgent:
    name = "commissioning"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("commissioning") or {}
        if c.get("required") is False:
            return GateResult(self.name, "PASS", "Cx/TAB not required this gate", {"commissioning": c})
        miss = _missing(c, ("prefunctional_complete", "tab_signed", "cxa_signed"))
        if miss:
            return GateResult(self.name, "HOLD", "Commissioning incomplete: " + ", ".join(miss), {"commissioning": c})
        return GateResult(self.name, "PASS", "Commissioning/TAB clear", {"commissioning": c})


class NcrCloseoutAgent:
    name = "ncr-closeout"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        n = ctx.get("ncr") or {}
        open_high = list(n.get("open_high_risk") or [])
        if open_high:
            return GateResult(self.name, "HOLD", "Open high-risk NCRs: " + ", ".join(open_high[:8]), {"ncr": n})
        if n.get("reinspect_pending"):
            return GateResult(self.name, "HOLD", "NCR reinspection pending", {"ncr": n})
        return GateResult(self.name, "PASS", "NCR closeout clear", {"ncr": n})


class AsbuiltsOmAgent:
    name = "asbuilts-om"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("docs") or {}
        miss = _missing(a, ("asbuilts_current", "om_complete", "warranty_log"))
        if miss:
            return GateResult(self.name, "HOLD", "Docs incomplete: " + ", ".join(miss), {"docs": a})
        return GateResult(self.name, "PASS", "As-builts/O&M/warranties clear", {"docs": a})


class TurnoverPackageAgent:
    name = "turnover-package"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("turnover") or {}
        miss = _missing(t, ("inspection_log", "ncr_summary", "certs_packaged", "photos_packaged"))
        if miss:
            return GateResult(self.name, "HOLD", "Turnover package incomplete: " + ", ".join(miss), {"turnover": t})
        return GateResult(self.name, "PASS", "Turnover package assembled", {"turnover": t})


class SignatureChainAgent:
    name = "signature-chain"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("signatures") or {}
        missing = list(s.get("missing_roles") or [])
        if missing:
            return GateResult(self.name, "HOLD", "Missing signatures: " + ", ".join(missing), {"signatures": s})
        if not s.get("chain_complete"):
            return GateResult(self.name, "HOLD", "Signature chain incomplete", {"signatures": s})
        return GateResult(self.name, "PASS", "Signature chain complete", {"signatures": s})


class AhjTcoAgent:
    name = "ahj-tco"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("tco") or {}
        if not a.get("mock_walk_complete"):
            return GateResult(self.name, "HOLD", "Mock TCO/AHJ walk not complete", {"tco": a})
        if a.get("open_occupancy_rfis"):
            return GateResult(self.name, "HOLD", "Open occupancy RFIs: " + ", ".join(a["open_occupancy_rfis"][:8]), {"tco": a})
        if not a.get("binder_ready"):
            return GateResult(self.name, "HOLD", "TCO binder/evidence not ready", {"tco": a})
        return GateResult(self.name, "PASS", "TCO/AHJ readiness clear", {"tco": a})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("life_safety", {}).get("egress_blocked"):
            violations.append("blocked egress")
        if ctx.get("life_safety", {}).get("emergency_lighting_failed"):
            violations.append("failed emergency lighting")
        if ctx.get("handoff", {}).get("attempted_with_life_safety_ncr"):
            violations.append("handoff with open life-safety NCR")
        if violations:
            return GateResult(self.name, "FAIL", "STOP-OCCUPY/HANDOFF: " + "; ".join(violations), {"violations": violations})
        return GateResult(self.name, "PASS", "No fail-safe violations", {})


class CrewOpsAgent:
    name = "crew-ops"

    def evaluate(self, ctx: dict[str, Any], require_briefing: bool = True) -> GateResult:
        crew = ctx.get("crew") or {}
        roles = set(crew.get("roles") or [])
        required = list(ERECT_ROLES)
        if (ctx.get("commissioning") or {}).get("required"):
            if "cx_rep" not in roles:
                required.append("cx_rep")
        missing = [r for r in required if r not in roles]
        if missing:
            return GateResult(self.name, "HOLD", "Missing roles: " + ", ".join(missing), {"missing": missing})
        if require_briefing and not crew.get("briefing_complete"):
            return GateResult(self.name, "HOLD", "Closeout walk briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Crew ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-closeout QA hold points clear", {})
        if phase != "pre" and q.get("closeout_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class CloseoutLeadAgent:
    name = "closeout-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked occupy/handoff"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
