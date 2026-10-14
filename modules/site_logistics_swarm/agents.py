"""Deterministic specialist gates for Site Logistics."""
from __future__ import annotations
from typing import Any
from modules.site_logistics_swarm.schemas import GateResult

ERECT_ROLES = ('logistics_lead', 'gate_guard', 'forklift_op', 'rigger_spotter', 'traffic_flagger', 'qc_tech', 'safety_watch')

def _num(v, default=None):
    if v is None: return default
    try: return float(v)
    except (TypeError, ValueError): return default

class AccessGatesAgent:
    name = "access-gates"
    def evaluate(self, ctx):
        a = ctx.get("access") or {}
        if a.get("gate_blocked"):
            return GateResult(self.name, "HOLD", "Gate/access blocked for delivery", {"access": a})
        if a.get("window_ok") is False:
            return GateResult(self.name, "HOLD", "Outside booked delivery window", {"access": a})
        if a.get("permit_ok") is False:
            return GateResult(self.name, "HOLD", "Street/crane permit incomplete", {"access": a})
        return GateResult(self.name, "PASS", "Access/gates clear", {"access": a})

class LaydownZonesAgent:
    name = "laydown-zones"
    def evaluate(self, ctx):
        l = ctx.get("laydown") or {}
        if l.get("aisle_blocked"):
            return GateResult(self.name, "FAIL", "Access aisle blocked — pause/reroute drop", {"laydown": l})
        if not l.get("zone_assigned"):
            return GateResult(self.name, "HOLD", "No laydown zone assigned", {"laydown": l})
        return GateResult(self.name, "PASS", "Laydown zone clear", {"laydown": l})

class FloorLiveLoadAgent:
    name = "floor-live-load"
    def evaluate(self, ctx):
        f = ctx.get("floor_load") or {}
        load = _num(f.get("staged_psf")); rating = _num(f.get("rating_psf"))
        if f.get("overload"):
            return GateResult(self.name, "FAIL", "Floor live-load overload", {"floor_load": f})
        if load is not None and rating is not None and load > rating:
            return GateResult(self.name, "FAIL", f"Staged {load} psf > rating {rating} psf", {"floor_load": f})
        if f.get("drywall_overstack"):
            return GateResult(self.name, "HOLD", "Drywall stacked >3 bundles or on edge", {"floor_load": f})
        if f.get("spread_ok") is False:
            return GateResult(self.name, "HOLD", "Pallet loads not spread on platforms", {"floor_load": f})
        return GateResult(self.name, "PASS", "Floor live-load clear", {"floor_load": f})

class MaterialMoveAgent:
    name = "material-move"
    def evaluate(self, ctx):
        m = ctx.get("material") or {}
        wt = _num(m.get("unit_weight_lb"))
        if wt is not None and wt > 100 and not (m.get("two_person") or m.get("lift_assist")):
            return GateResult(self.name, "HOLD", f"Unit {wt} lb needs 2-person/assist", {"material": m})
        if m.get("method") is None and m.get("required") is not False:
            return GateResult(self.name, "HOLD", "Delivery/lift method not set", {"material": m})
        return GateResult(self.name, "PASS", "Material move method clear", {"material": m})

class LiftPathAgent:
    name = "lift-path"
    def evaluate(self, ctx):
        p = ctx.get("lift_path") or {}
        if p.get("conflict"):
            return GateResult(self.name, "HOLD", "Lift path conflicts with other trades", {"lift_path": p})
        if p.get("reserved") is False:
            return GateResult(self.name, "HOLD", "Elevator/hoist/crane path not reserved", {"lift_path": p})
        return GateResult(self.name, "PASS", "Lift path clear", {"lift_path": p})

class CraneSwingAgent:
    name = "crane-swing"
    def evaluate(self, ctx):
        c = ctx.get("crane") or {}
        if c.get("required") is False:
            return GateResult(self.name, "SKIP", "No crane logistics drop", {})
        if c.get("people_in_swing"):
            return GateResult(self.name, "FAIL", "Personnel in crane swing path", {"crane": c})
        if c.get("exclusion_marked") is False:
            return GateResult(self.name, "HOLD", "Crane exclusion not marked", {"crane": c})
        return GateResult(self.name, "PASS", "Crane swing logistics clear", {"crane": c})

class TrafficControlAgent:
    name = "traffic-control"
    def evaluate(self, ctx):
        t = ctx.get("traffic") or {}
        if t.get("ped_vehicle_conflict"):
            return GateResult(self.name, "HOLD", "Uncontrolled vehicle/pedestrian conflict", {"traffic": t})
        if t.get("routes_marked") is False:
            return GateResult(self.name, "HOLD", "Pedestrian/vehicle routes not marked", {"traffic": t})
        return GateResult(self.name, "PASS", "Traffic control clear", {"traffic": t})

class TempPowerAgent:
    name = "temp-power"
    def evaluate(self, ctx):
        p = ctx.get("temp_power") or {}
        if p.get("required") is False:
            return GateResult(self.name, "SKIP", "Temp power not in this gate", {})
        if p.get("daisy_chain"):
            return GateResult(self.name, "FAIL", "Daisy-chained extension cords", {"temp_power": p})
        if p.get("gfci") is False:
            return GateResult(self.name, "HOLD", "GFCI missing on temp outlets", {"temp_power": p})
        return GateResult(self.name, "PASS", "Temp power clear", {"temp_power": p})

class TempHeatWaterAgent:
    name = "temp-heat-water"
    def evaluate(self, ctx):
        h = ctx.get("temp_heat_water") or {}
        if h.get("required") is False:
            return GateResult(self.name, "SKIP", "Temp heat/water not in this gate", {})
        if h.get("open_flame_undesignated"):
            return GateResult(self.name, "FAIL", "Open-flame heat outside designated zone", {"temp_heat_water": h})
        if h.get("co_monitor") is False and h.get("heat_active"):
            return GateResult(self.name, "HOLD", "CO monitor missing near temp heat", {"temp_heat_water": h})
        if h.get("backflow") is False and h.get("water_active"):
            return GateResult(self.name, "HOLD", "Temp water missing backflow prevention", {"temp_heat_water": h})
        return GateResult(self.name, "PASS", "Temp heat/water clear", {"temp_heat_water": h})

class InventoryQrAgent:
    name = "inventory-qr"
    def evaluate(self, ctx):
        i = ctx.get("inventory") or {}
        if i.get("untagged_critical"):
            return GateResult(self.name, "HOLD", "Critical materials untagged in shared laydown", {"inventory": i})
        if i.get("jit_mismatch"):
            return GateResult(self.name, "HOLD", "JIT delivery mismatch vs trade schedule", {"inventory": i})
        return GateResult(self.name, "PASS", "Inventory/QR clear", {"inventory": i})

class HazardZonesAgent:
    name = "hazard-zones"
    def evaluate(self, ctx):
        h = ctx.get("hazard") or {}
        if h.get("red_uncontrolled_staging"):
            return GateResult(self.name, "FAIL", "Staging in uncontrolled red hazard zone", {"hazard": h})
        return GateResult(self.name, "PASS", "Hazard zones respected", {"hazard": h})

class WasteHousekeepingAgent:
    name = "waste-housekeeping"
    def evaluate(self, ctx):
        w = ctx.get("housekeeping") or {}
        if w.get("egress_blocked"):
            return GateResult(self.name, "FAIL", "Emergency egress blocked by debris/materials", {"housekeeping": w})
        if w.get("aisle_debris"):
            return GateResult(self.name, "HOLD", "Aisle trip hazards / debris present", {"housekeeping": w})
        return GateResult(self.name, "PASS", "Housekeeping clear", {"housekeeping": w})

class SafetyFailsafeAgent:
    name = "safety-failsafe"
    def evaluate(self, ctx):
        s = ctx.get("safety") or {}; violations = list(s.get("violations") or [])
        f = ctx.get("floor_load") or {}
        load = _num(f.get("staged_psf")); rating = _num(f.get("rating_psf"))
        if f.get("overload") or (load is not None and rating is not None and load > rating):
            violations.append("floor live-load overload")
        if (ctx.get("crane") or {}).get("people_in_swing"):
            violations.append("personnel in crane swing")
        if (ctx.get("laydown") or {}).get("aisle_blocked") and (ctx.get("housekeeping") or {}).get("egress_blocked"):
            violations.append("blocked aisle/egress")
        elif (ctx.get("housekeeping") or {}).get("egress_blocked"):
            violations.append("blocked emergency egress")
        elif (ctx.get("laydown") or {}).get("aisle_blocked"):
            violations.append("critical aisle blocked")
        if (ctx.get("temp_power") or {}).get("daisy_chain"):
            violations.append("daisy-chained temp power")
        if (ctx.get("temp_heat_water") or {}).get("open_flame_undesignated"):
            violations.append("unsafe open-flame temp heat")
        if (ctx.get("hazard") or {}).get("red_uncontrolled_staging"):
            violations.append("staging in red hazard zone")
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
            return GateResult(self.name, "HOLD", "Logistics briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Logistics crew ready headcount={crew.get('headcount', len(roles))}", {})

class QaInspectorAgent:
    name = "qa-inspector"
    def evaluate(self, ctx, phase="pre"):
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-delivery docs clear", {})
        if phase == "closeout" and q.get("closeout_clear"):
            return GateResult(self.name, "PASS", "Logistics closeout docs clear", {})
        if phase not in ("pre",) and q.get("tickets_clear"):
            return GateResult(self.name, "PASS", f"{phase} logistics docs clear", {})
        return GateResult(self.name, "HOLD", f"No logistics QA evidence for phase={phase}", {"qa": q})

class LogisticsLeadAgent:
    name = "logistics-lead"
    def assemble(self, ctx, gates, workflow):
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked logistics sequence"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Logistics sequence ready for {ctx.get('zone_id', ctx.get('drop_id', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
