"""Named Site Logistics workflow runners."""
from __future__ import annotations
from typing import Any, Callable
from modules.site_logistics_swarm.agents import (
    AccessGatesAgent, CraneSwingAgent, CrewOpsAgent, FloorLiveLoadAgent, HazardZonesAgent,
    InventoryQrAgent, LaydownZonesAgent, LiftPathAgent, LogisticsLeadAgent, MaterialMoveAgent,
    QaInspectorAgent, SafetyFailsafeAgent, TempHeatWaterAgent, TempPowerAgent, TrafficControlAgent,
    WasteHousekeepingAgent,
)
from modules.site_logistics_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-delivery-gate", "access-window-gate", "laydown-aisle-gate", "floor-load-gate",
    "material-move-gate", "lift-path-gate", "crane-drop-gate", "temp-utilities-gate",
    "traffic-control-gate", "jit-inventory-gate", "end-of-day-housekeeping", "hold-abort",
)

def _decide(gates):
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.status == "FAIL" for g in active): return "ABORT"
    if any(g.status in ("FAIL", "HOLD") for g in active): return "HOLD"
    return "GO"

def _actions(decision, gates):
    if decision == "GO":
        return ["Proceed with delivery/staging under logistics plan", "Keep aisles and egress clear; re-check loads"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP DROP — secure load, clear people, restore aisle/egress",
            "Preserve tickets, photos, load calcs, timestamps",
            "Re-enter through pre-delivery-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "logistics-lead"]
    return ["Do not stage/drop until cleared",
            *[f"Clear {g.agent}: {g.detail}" for g in holds],
            "Re-run failed gates + safety-failsafe before release"]

def _id(ctx):
    return ctx.get("zone_id") or ctx.get("drop_id") or ctx.get("area") or "ZONE-UNSET"

class WorkflowRunner:
    def __init__(self):
        self.access = AccessGatesAgent(); self.laydown = LaydownZonesAgent()
        self.floor = FloorLiveLoadAgent(); self.material = MaterialMoveAgent()
        self.path = LiftPathAgent(); self.crane = CraneSwingAgent()
        self.traffic = TrafficControlAgent(); self.power = TempPowerAgent()
        self.heat = TempHeatWaterAgent(); self.inv = InventoryQrAgent()
        self.hazard = HazardZonesAgent(); self.waste = WasteHousekeepingAgent()
        self.safety = SafetyFailsafeAgent(); self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent(); self.lead = LogisticsLeadAgent()

    def _finish(self, workflow, ctx, gates, summaries):
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_delivery_gate(self, ctx):
        gates = [self.access.evaluate(ctx), self.laydown.evaluate(ctx), self.floor.evaluate(ctx),
                 self.crew.evaluate(ctx, True), self.safety.evaluate(ctx), self.qa.evaluate(ctx, "pre")]
        return self._finish("pre-delivery-gate", ctx, gates, {
            "GO": "Pre-delivery clear — drop/staging may proceed.",
            "HOLD": "Pre-delivery holding — access/laydown/load.",
            "ABORT": "Pre-delivery aborted by fail-safe.",
        })

    def access_window_gate(self, ctx):
        gates = [self.access.evaluate(ctx), self.traffic.evaluate(ctx),
                 self.qa.evaluate(ctx, "during"), self.safety.evaluate(ctx)]
        return self._finish("access-window-gate", ctx, gates, {
            "GO": "Access window clear.", "HOLD": "Access window holding.", "ABORT": "Access window aborted.",
        })

    def laydown_aisle_gate(self, ctx):
        gates = [self.laydown.evaluate(ctx), self.hazard.evaluate(ctx), self.waste.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("laydown-aisle-gate", ctx, gates, {
            "GO": "Laydown/aisles clear.", "HOLD": "Laydown/aisles holding.",
            "ABORT": "Laydown/aisles aborted — clear path.",
        })

    def floor_load_gate(self, ctx):
        gates = [self.floor.evaluate(ctx), self.material.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("floor-load-gate", ctx, gates, {
            "GO": "Floor load clear.", "HOLD": "Floor load holding.", "ABORT": "Floor load aborted — unload/spread.",
        })

    def material_move_gate(self, ctx):
        gates = [self.material.evaluate(ctx), self.path.evaluate(ctx), self.floor.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("material-move-gate", ctx, gates, {
            "GO": "Material move clear.", "HOLD": "Material move holding.", "ABORT": "Material move aborted.",
        })

    def lift_path_gate(self, ctx):
        gates = [self.path.evaluate(ctx), self.crane.evaluate(ctx), self.traffic.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("lift-path-gate", ctx, gates, {
            "GO": "Lift path clear.", "HOLD": "Lift path holding.", "ABORT": "Lift path aborted.",
        })

    def crane_drop_gate(self, ctx):
        ctx = {**ctx, "crane": {**(ctx.get("crane") or {}), "required": True}}
        gates = [self.crane.evaluate(ctx), self.path.evaluate(ctx), self.laydown.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("crane-drop-gate", ctx, gates, {
            "GO": "Crane drop clear.", "HOLD": "Crane drop holding.",
            "ABORT": "Crane drop aborted — clear swing path.",
        })

    def temp_utilities_gate(self, ctx):
        ctx = {**ctx,
               "temp_power": {**(ctx.get("temp_power") or {}), "required": True},
               "temp_heat_water": {**(ctx.get("temp_heat_water") or {}), "required": True}}
        gates = [self.power.evaluate(ctx), self.heat.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("temp-utilities-gate", ctx, gates, {
            "GO": "Temp utilities clear.", "HOLD": "Temp utilities holding.", "ABORT": "Temp utilities aborted.",
        })

    def traffic_control_gate(self, ctx):
        gates = [self.traffic.evaluate(ctx), self.access.evaluate(ctx),
                 self.safety.evaluate(ctx), self.qa.evaluate(ctx, "during")]
        return self._finish("traffic-control-gate", ctx, gates, {
            "GO": "Traffic control clear.", "HOLD": "Traffic control holding.", "ABORT": "Traffic control aborted.",
        })

    def jit_inventory_gate(self, ctx):
        gates = [self.inv.evaluate(ctx), self.laydown.evaluate(ctx), self.access.evaluate(ctx),
                 self.qa.evaluate(ctx, "during")]
        return self._finish("jit-inventory-gate", ctx, gates, {
            "GO": "JIT/inventory clear.", "HOLD": "JIT/inventory holding.", "ABORT": "JIT/inventory aborted.",
        })

    def end_of_day_housekeeping(self, ctx):
        gates = [self.waste.evaluate(ctx), self.laydown.evaluate(ctx), self.power.evaluate(ctx),
                 self.qa.evaluate(ctx, "closeout"), self.crew.evaluate(ctx, False)]
        return self._finish("end-of-day-housekeeping", ctx, gates, {
            "GO": "End-of-day housekeeping clear.", "HOLD": "Housekeeping holding.", "ABORT": "Housekeeping aborted.",
        })

    def hold_abort(self, ctx):
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult("logistics-lead", "FAIL" if decision == "ABORT" else "HOLD", reason,
                            {"owner": ctx.get("owner", "logistics_superintendent")})]
        summary = "ABORT escalated — stop drop and clear site path." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))

def get_workflow_handlers(runner=None):
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
