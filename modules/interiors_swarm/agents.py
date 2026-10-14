"""Deterministic specialist gates for interiors / drywall / shafts."""

from __future__ import annotations

from typing import Any

from modules.interiors_swarm.schemas import GateResult

ERECT_ROLES = ('interiors_lead', 'framer', 'hanger', 'taper', 'shaft_tech', 'qc_tech', 'safety_watch')


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class MaterialsSubmittalAgent:
    name = "materials-submittal"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("materials") or {}
        miss = _missing(m, ("studs_approved", "board_approved", "assemblies_approved"))
        if miss:
            return GateResult(self.name, "HOLD", "Materials incomplete: " + ", ".join(miss), {"materials": m})
        return GateResult(self.name, "PASS", "Stud/board/assembly submittals clear", {"materials": m})


class LayoutControlAgent:
    name = "layout-control"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("layout") or {}
        miss = _missing(l, ("control_lines", "openings_set"))
        if miss:
            return GateResult(self.name, "HOLD", "Layout incomplete: " + ", ".join(miss), {"layout": l})
        if l.get("conflicts"):
            return GateResult(self.name, "HOLD", "Layout conflicts: " + ", ".join(l["conflicts"]), {"layout": l})
        return GateResult(self.name, "PASS", "Layout/control clear", {"layout": l})


class MetalStudFramingAgent:
    name = "metal-stud-framing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("framing") or {}
        if f.get("spacing_ok") is False or f.get("gauge_ok") is False:
            return GateResult(self.name, "HOLD", "Stud spacing/gauge not per shops", {"framing": f})
        if f.get("plumb_ok") is False:
            return GateResult(self.name, "HOLD", "Framing plumb/plane out of tolerance", {"framing": f})
        if f.get("bracing_ok") is False:
            return GateResult(self.name, "HOLD", "Bridging/bracing/deflection track incomplete", {"framing": f})
        return GateResult(self.name, "PASS", "Metal stud framing clear", {"framing": f})


class ShaftwallAgent:
    name = "shaftwall"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("shaftwall") or {}
        if s.get("required") is False:
            return GateResult(self.name, "SKIP", "No shaftwall scope", {})
        if not s.get("ul_design_match"):
            return GateResult(self.name, "HOLD", "Shaftwall not matching UL design", {"shaftwall": s})
        if s.get("liner_continuous") is False:
            return GateResult(self.name, "HOLD", "Shaft liner not continuous/sealed", {"shaftwall": s})
        if s.get("penetrations_open"):
            return GateResult(self.name, "HOLD", "Shaft penetrations open before close", {"shaftwall": s})
        return GateResult(self.name, "PASS", "Shaftwall clear", {"shaftwall": s})


class AcousticsStcAgent:
    name = "acoustics-stc"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("acoustics") or {}
        if a.get("required") is False:
            return GateResult(self.name, "PASS", "STC not required this zone", {"acoustics": a})
        if not a.get("assembly_match"):
            return GateResult(self.name, "HOLD", "STC assembly does not match specified design", {"acoustics": a})
        if a.get("seals_ok") is False:
            return GateResult(self.name, "HOLD", "Acoustic seals incomplete", {"acoustics": a})
        if a.get("flanking"):
            return GateResult(self.name, "HOLD", "Flanking path shorts identified", {"acoustics": a})
        return GateResult(self.name, "PASS", "Acoustics/STC clear", {"acoustics": a})


class FireRatedAssembliesAgent:
    name = "fire-rated-assemblies"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("fire_rated") or {}
        if f.get("required") is False:
            return GateResult(self.name, "PASS", "No fire-rated assembly this gate", {"fire_rated": f})
        if not f.get("ul_design_match"):
            return GateResult(self.name, "HOLD", "Fire assembly UL/GA design mismatch", {"fire_rated": f})
        if f.get("layers_ok") is False or f.get("fastener_pattern_ok") is False:
            return GateResult(self.name, "HOLD", "Layer count/fastener pattern deficient", {"fire_rated": f})
        if f.get("head_of_wall_ok") is False:
            return GateResult(self.name, "HOLD", "Head-of-wall firestopping incomplete", {"fire_rated": f})
        if f.get("compromised"):
            return GateResult(self.name, "FAIL", "Fire-rated assembly compromised", {"fire_rated": f})
        return GateResult(self.name, "PASS", "Fire-rated assemblies clear", {"fire_rated": f})


class BlockingBackingAgent:
    name = "blocking-backing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("blocking") or {}
        if b.get("required") is False:
            return GateResult(self.name, "PASS", "No special blocking this gate", {"blocking": b})
        if b.get("missing"):
            return GateResult(self.name, "HOLD", "Missing blocking: " + ", ".join(b["missing"]), {"blocking": b})
        if not b.get("documented"):
            return GateResult(self.name, "HOLD", "Blocking not documented before cover", {"blocking": b})
        return GateResult(self.name, "PASS", "Blocking/backing clear", {"blocking": b})


class BoardHangAgent:
    name = "board-hang"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("board") or {}
        if b.get("type_ok") is False:
            return GateResult(self.name, "HOLD", "Wrong board type on assembly", {"board": b})
        if b.get("fasteners_ok") is False:
            return GateResult(self.name, "HOLD", "Fastener pattern/set deficient", {"board": b})
        if b.get("damaged_left"):
            return GateResult(self.name, "HOLD", "Damaged board left in place", {"board": b})
        return GateResult(self.name, "PASS", "Board hang clear", {"board": b})


class TapingFinishAgent:
    name = "taping-finish"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("finish") or {}
        if t.get("level_met") is False:
            return GateResult(self.name, "HOLD", f"Finish level not met (need {t.get('required_level', '?')})", {"finish": t})
        if t.get("defects"):
            return GateResult(self.name, "HOLD", "Finish defects: " + ", ".join(t["defects"]), {"finish": t})
        if not t.get("dry"):
            return GateResult(self.name, "HOLD", "Joints not dry for next coat/paint", {"finish": t})
        return GateResult(self.name, "PASS", "Taping/finish clear", {"finish": t})


class OpeningsDoorsAgent:
    name = "openings-doors"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        o = ctx.get("openings") or {}
        if o.get("required") is False:
            return GateResult(self.name, "SKIP", "No openings scope", {})
        if o.get("plumb_square") is False:
            return GateResult(self.name, "HOLD", "Frames not plumb/square", {"openings": o})
        if o.get("rated_unlabeled"):
            return GateResult(self.name, "HOLD", "Fire-rated frames unlabeled/mismatched", {"openings": o})
        return GateResult(self.name, "PASS", "Openings/doors clear", {"openings": o})


class InwallCoverReleaseAgent:
    name = "inwall-cover-release"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        i = ctx.get("inwall") or {}
        if not i.get("mep_signed"):
            return GateResult(self.name, "HOLD", "In-wall MEP inspection not signed", {"inwall": i})
        if not i.get("firestop_photos"):
            return GateResult(self.name, "HOLD", "Firestop photo log incomplete before cover", {"inwall": i})
        if i.get("open_ncrs"):
            return GateResult(self.name, "HOLD", "Open in-wall NCRs: " + ", ".join(i["open_ncrs"]), {"inwall": i})
        return GateResult(self.name, "PASS", "In-wall cover release clear", {"inwall": i})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No environmental data", {})
        holds = []
        if w.get("high_humidity") and not w.get("building_dry"):
            holds.append("high humidity / building not dry-in")
        if w.get("freezing") and not w.get("heat_for_mud"):
            holds.append("freeze risk for compound without heat")
        if w.get("wet_board_storage"):
            holds.append("board stored wet/warped")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Environment CLEAR", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("scaffold") or {}).get("unsafe"):
            violations.append("unsafe scaffold/lift/stilts")
        if (ctx.get("fire_rated") or {}).get("compromised"):
            violations.append("fire-rated shaft/assembly compromised")
        if (ctx.get("egress") or {}).get("blocked"):
            violations.append("egress path blocked by staging")
        if (ctx.get("hot_work") or {}).get("no_permit"):
            violations.append("hot work without permit")
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
            return GateResult(self.name, "PASS", "Pre-interiors QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class InteriorsLeadAgent:
    name = "interiors-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked interiors work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
