"""Deterministic specialist gates for Roofing QAQC."""
from __future__ import annotations
from typing import Any
from modules.roofing_swarm.schemas import GateResult

ERECT_ROLES = ('roof_lead', 'deck_hand', 'shingler', 'flasher', 'membrane_tech', 'qc_tech', 'safety_watch')

def _num(v, default=None):
    if v is None: return default
    try: return float(v)
    except (TypeError, ValueError): return default

class DeckPrepAgent:
    name = "deck-prep"
    def evaluate(self, ctx):
        d = ctx.get("deck") or {}
        if d.get("wet") or d.get("unsound"):
            return GateResult(self.name, "HOLD", "Deck wet or unsound", {"deck": d})
        if d.get("fastened") is False:
            return GateResult(self.name, "HOLD", "Sheathing not properly fastened", {"deck": d})
        return GateResult(self.name, "PASS", "Deck prep clear", {"deck": d})

class UnderlaymentAgent:
    name = "underlayment"
    def evaluate(self, ctx):
        u = ctx.get("underlayment") or {}
        if u.get("required") is False:
            return GateResult(self.name, "SKIP", "Underlayment N/A for this system", {})
        if u.get("bridging") or u.get("wrinkles"):
            return GateResult(self.name, "HOLD", "Underlayment bridges/wrinkles (bubbles)", {"underlayment": u})
        if u.get("laps_ok") is False:
            return GateResult(self.name, "HOLD", "Underlayment laps short of 3in/6in pattern", {"underlayment": u})
        return GateResult(self.name, "PASS", "Underlayment clear", {"underlayment": u})

class IceWaterShieldAgent:
    name = "ice-water-shield"
    def evaluate(self, ctx):
        z = ctx.get("zone") or {}; i = ctx.get("ice_water") or {}
        if not z.get("ice_damming_risk") and not i.get("required"):
            return GateResult(self.name, "SKIP", "Ice/water shield not required", {})
        if i.get("installed") is False:
            return GateResult(self.name, "FAIL", "Ice/water shield missing in required ice zone", {"ice_water": i})
        if i.get("coverage_ok") is False:
            return GateResult(self.name, "HOLD", "Ice/water coverage incomplete at eaves", {"ice_water": i})
        return GateResult(self.name, "PASS", "Ice/water shield clear", {"ice_water": i})

class FastenerPatternAgent:
    name = "fastener-pattern"
    def evaluate(self, ctx):
        f = ctx.get("fasteners") or {}; z = ctx.get("zone") or {}
        if f.get("staples") and not f.get("manufacturer_variance"):
            return GateResult(self.name, "FAIL", "Staples used without manufacturer variance", {"fasteners": f})
        nails = _num(f.get("nails_per_shingle"))
        need = 6 if z.get("high_wind") or z.get("coastal") else 4
        if nails is not None and nails < need:
            return GateResult(self.name, "FAIL", f"Nail count {nails} < required {need}", {"fasteners": f})
        if f.get("skippers") or int(f.get("overdriven_consecutive") or 0) > 3:
            return GateResult(self.name, "FAIL", "Skippers or >3 consecutive overdriven nails", {"fasteners": f})
        if f.get("flush_ok") is False or f.get("penetration_ok") is False:
            return GateResult(self.name, "HOLD", "Nails not flush or penetration < 3/4in", {"fasteners": f})
        return GateResult(self.name, "PASS", "Fastener pattern clear", {"fasteners": f})

class ShinglePlacementAgent:
    name = "shingle-placement"
    def evaluate(self, ctx):
        s = ctx.get("shingles") or {}
        if s.get("system") == "membrane" or s.get("required") is False:
            return GateResult(self.name, "SKIP", "Shingle placement N/A", {})
        if s.get("starter_strip") is False:
            return GateResult(self.name, "FAIL", "No starter strip at eave", {"shingles": s})
        if s.get("offset_ok") is False or s.get("stacked_joints"):
            return GateResult(self.name, "HOLD", "Bad stagger / stacked vertical joints", {"shingles": s})
        if s.get("exposure_ok") is False:
            return GateResult(self.name, "HOLD", "Shingle exposure outside manufacturer tolerance", {"shingles": s})
        return GateResult(self.name, "PASS", "Shingle placement clear", {"shingles": s})

class FlashingDetailsAgent:
    name = "flashing-details"
    def evaluate(self, ctx):
        f = ctx.get("flashing") or {}
        if f.get("step_missing") or f.get("headwall_missing"):
            return GateResult(self.name, "FAIL", "Critical step/headwall flashing missing", {"flashing": f})
        if f.get("interwoven") is False or f.get("wall_overlap_ok") is False:
            return GateResult(self.name, "HOLD", "Step flashing not interwoven or <4in up wall", {"flashing": f})
        return GateResult(self.name, "PASS", "Flashing details clear", {"flashing": f})

class ValleyFlashingAgent:
    name = "valley-flashing"
    def evaluate(self, ctx):
        v = ctx.get("valley") or {}
        if v.get("present") is False:
            return GateResult(self.name, "SKIP", "No valleys on this roof", {})
        if v.get("flashed") is False:
            return GateResult(self.name, "FAIL", "Valley without proper flashing", {"valley": v})
        if v.get("exposed_fasteners_in_path"):
            return GateResult(self.name, "HOLD", "Exposed fasteners in valley water path", {"valley": v})
        return GateResult(self.name, "PASS", "Valley flashing clear", {"valley": v})

class PenetrationsBootsAgent:
    name = "penetrations-boots"
    def evaluate(self, ctx):
        p = ctx.get("penetrations") or {}
        if p.get("present") is False:
            return GateResult(self.name, "SKIP", "No penetrations", {})
        if p.get("unsealed") or p.get("caulk_only"):
            return GateResult(self.name, "FAIL", "Unsealed / caulk-only penetration boots", {"penetrations": p})
        if p.get("boots_centered") is False:
            return GateResult(self.name, "HOLD", "Pipe boots not centered/seated", {"penetrations": p})
        return GateResult(self.name, "PASS", "Penetrations/boots clear", {"penetrations": p})

class RidgeVentAgent:
    name = "ridge-vent"
    def evaluate(self, ctx):
        r = ctx.get("ridge") or {}
        if r.get("required") is False:
            return GateResult(self.name, "SKIP", "Ridge vent not specified", {})
        if r.get("unsealed_slot"):
            return GateResult(self.name, "HOLD", "Unsealed ridge vent exposure", {"ridge": r})
        if r.get("caps_secured") is False or r.get("vent_continuous") is False:
            return GateResult(self.name, "HOLD", "Ridge caps/vent incomplete", {"ridge": r})
        return GateResult(self.name, "PASS", "Ridge/vent clear", {"ridge": r})

class MembraneFlatAgent:
    name = "membrane-flat"
    def evaluate(self, ctx):
        m = ctx.get("membrane") or {}; system = (ctx.get("shingles") or {}).get("system")
        if not m.get("required") and system != "membrane":
            return GateResult(self.name, "SKIP", "Flat membrane not in scope", {})
        if m.get("open_seams"):
            return GateResult(self.name, "FAIL", "Open/untested membrane seams", {"membrane": m})
        if m.get("drainage_clear") is False:
            return GateResult(self.name, "HOLD", "Drainage/overflow blocked", {"membrane": m})
        if m.get("flashings_ok") is False:
            return GateResult(self.name, "HOLD", "Membrane wall/penetration flashings incomplete", {"membrane": m})
        return GateResult(self.name, "PASS", "Membrane/flat roof clear", {"membrane": m})

class HighWindZoneAgent:
    name = "high-wind-zone"
    def evaluate(self, ctx):
        z = ctx.get("zone") or {}; f = ctx.get("fasteners") or {}
        if not z.get("high_wind") and not z.get("coastal"):
            return GateResult(self.name, "SKIP", "Not a high-wind/coastal zone", {})
        nails = _num(f.get("nails_per_shingle"), 0) or 0
        if nails < 6 and (ctx.get("shingles") or {}).get("system") != "membrane":
            return GateResult(self.name, "HOLD", "High-wind zone needs enhanced (6-nail) fastening", {"zone": z, "fasteners": f})
        if f.get("enhanced") is False:
            return GateResult(self.name, "HOLD", "Enhanced wind fastening not verified", {"zone": z})
        return GateResult(self.name, "PASS", "High-wind fastening clear", {"zone": z})

class SafetyFallAgent:
    name = "safety-fall"
    def evaluate(self, ctx):
        s = ctx.get("fall_protection") or {}
        if s.get("unprotected_edge"):
            return GateResult(self.name, "FAIL", "Unprotected work at roof edge", {"fall_protection": s})
        if s.get("controls_ok") is False:
            return GateResult(self.name, "HOLD", "Fall protection controls incomplete", {"fall_protection": s})
        return GateResult(self.name, "PASS", "Roof fall protection clear", {"fall_protection": s})

class SafetyFailsafeAgent:
    name = "safety-failsafe"
    def evaluate(self, ctx):
        s = ctx.get("safety") or {}; violations = list(s.get("violations") or [])
        f = ctx.get("fasteners") or {}
        if f.get("staples") and not f.get("manufacturer_variance"):
            violations.append("staples without variance")
        if f.get("skippers") or int(f.get("overdriven_consecutive") or 0) > 3:
            violations.append("skippers/overdriven nail pattern")
        fl = ctx.get("flashing") or {}
        if fl.get("step_missing") or fl.get("headwall_missing"):
            violations.append("missing critical wall flashing")
        if (ctx.get("valley") or {}).get("present") and (ctx.get("valley") or {}).get("flashed") is False:
            violations.append("valley unflashed")
        if (ctx.get("shingles") or {}).get("starter_strip") is False and (ctx.get("shingles") or {}).get("system") != "membrane":
            violations.append("no starter strip")
        z = ctx.get("zone") or {}; iw = ctx.get("ice_water") or {}
        if (z.get("ice_damming_risk") or iw.get("required")) and iw.get("installed") is False:
            violations.append("ice/water missing in ice zone")
        p = ctx.get("penetrations") or {}
        if p.get("unsealed") or p.get("caulk_only"):
            violations.append("unsealed penetrations")
        if (ctx.get("membrane") or {}).get("open_seams"):
            violations.append("open membrane seams")
        if (ctx.get("fall_protection") or {}).get("unprotected_edge"):
            violations.append("unprotected roof edge")
        if violations:
            return GateResult(self.name, "FAIL", "STOP-WORK: " + "; ".join(dict.fromkeys(violations)), {"violations": list(dict.fromkeys(violations))})
        return GateResult(self.name, "PASS", "No fail-safe violations", {})

class CrewOpsAgent:
    name = "crew-ops"
    def evaluate(self, ctx, require_briefing=True):
        crew = ctx.get("crew") or {}; roles = set(crew.get("roles") or [])
        missing = [r for r in ERECT_ROLES if r not in roles]
        if missing:
            return GateResult(self.name, "HOLD", "Missing roles: " + ", ".join(missing), {"missing": missing})
        if require_briefing and not crew.get("briefing_complete"):
            return GateResult(self.name, "HOLD", "Roof briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Roof crew ready headcount={crew.get('headcount', len(roles))}", {})

class QaInspectorAgent:
    name = "qa-inspector"
    def evaluate(self, ctx, phase="pre"):
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-roof docs clear", {})
        if phase == "final" and q.get("final_punch_clear"):
            return GateResult(self.name, "PASS", "Final roof punch clear", {})
        if phase not in ("pre",) and q.get("photo_log_clear"):
            return GateResult(self.name, "PASS", f"{phase} roof docs clear", {})
        return GateResult(self.name, "HOLD", f"No roof QA evidence for phase={phase}", {"qa": q})

class RoofLeadAgent:
    name = "roof-lead"
    def assemble(self, ctx, gates, workflow):
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked roofing sequence"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Roofing sequence ready for {ctx.get('zone_id', ctx.get('roof_id', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
