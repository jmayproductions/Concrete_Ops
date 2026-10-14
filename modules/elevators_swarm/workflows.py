"""Named elevator / VTR workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.elevators_swarm.agents import (
    AhjInspectionAgent,
    CabInstallAgent,
    CrewOpsAgent,
    DoorEntranceAgent,
    ElectricalControllerAgent,
    ElevatorsLeadAgent,
    EquipmentSubmittalAgent,
    HoistwayClearanceAgent,
    PitMachineRoomAgent,
    QaInspectorAgent,
    RailPlumbAgent,
    SafetyDevicesAgent,
    SafetyFailsafeAgent,
    TemporaryRunAgent,
    TurnoverTrainingAgent,
    WeatherProtectAgent,
)
from modules.elevators_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-elevator-gate",
    "pit-machine-room-gate",
    "rail-install-runbook",
    "hoistway-clearance-gate",
    "door-entrance-gate",
    "cab-controller-gate",
    "safety-devices-gate",
    "temporary-run-gate",
    "ahj-inspection-gate",
    "weather-protect-gate",
    "elevator-turnover",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next elevator sequence / workflow", "Keep plumb logs + AHJ punch current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — barricade hoistway; restore safeties; pull temp-run authority",
            "Preserve photos, plumb sheets, AHJ notes, timestamps",
            "Re-enter through pre-elevator-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "elevators-lead"]
    return [
        "Do not energize / temp-run / turn over",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("car_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.equipment = EquipmentSubmittalAgent()
        self.pit = PitMachineRoomAgent()
        self.rails = RailPlumbAgent()
        self.hoistway = HoistwayClearanceAgent()
        self.doors = DoorEntranceAgent()
        self.cab = CabInstallAgent()
        self.electrical = ElectricalControllerAgent()
        self.devices = SafetyDevicesAgent()
        self.ahj = AhjInspectionAgent()
        self.temp = TemporaryRunAgent()
        self.turnover = TurnoverTrainingAgent()
        self.weather = WeatherProtectAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = ElevatorsLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_elevator_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.equipment.evaluate(ctx),
            self.pit.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-elevator-gate", ctx, gates, {
            "GO": "Pre-elevator clear — rail/equipment sequence may proceed.",
            "HOLD": "Pre-elevator holding — equipment/pit/weather.",
            "ABORT": "Pre-elevator aborted by fail-safe.",
        })

    def pit_machine_room_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.pit.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("pit-machine-room-gate", ctx, gates, {
            "GO": "Pit/machine room clear.",
            "HOLD": "Pit/machine room holding.",
            "ABORT": "Pit/machine room aborted.",
        })

    def rail_install_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.rails.evaluate(ctx),
            self.hoistway.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("rail-install-runbook", ctx, gates, {
            "GO": "Rail install clear.",
            "HOLD": "Rail install holding.",
            "ABORT": "Rail install aborted.",
        })

    def hoistway_clearance_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.hoistway.evaluate(ctx),
            self.rails.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("hoistway-clearance-gate", ctx, gates, {
            "GO": "Hoistway clearances clear.",
            "HOLD": "Hoistway clearances holding.",
            "ABORT": "Hoistway clearances aborted.",
        })

    def door_entrance_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.doors.evaluate(ctx),
            self.hoistway.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("door-entrance-gate", ctx, gates, {
            "GO": "Door/entrances clear.",
            "HOLD": "Door/entrances holding.",
            "ABORT": "Door/entrances aborted.",
        })

    def cab_controller_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.cab.evaluate(ctx),
            self.electrical.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("cab-controller-gate", ctx, gates, {
            "GO": "Cab/controller clear.",
            "HOLD": "Cab/controller holding.",
            "ABORT": "Cab/controller aborted.",
        })

    def safety_devices_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.devices.evaluate(ctx),
            self.doors.evaluate(ctx),
            self.electrical.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("safety-devices-gate", ctx, gates, {
            "GO": "Safety devices clear.",
            "HOLD": "Safety devices holding.",
            "ABORT": "Safety devices aborted — restore safeties.",
        })

    def temporary_run_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.temp.evaluate(ctx),
            self.devices.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("temporary-run-gate", ctx, gates, {
            "GO": "Temporary run controls clear.",
            "HOLD": "Temporary run holding.",
            "ABORT": "Temporary run aborted.",
        })

    def ahj_inspection_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.ahj.evaluate(ctx),
            self.devices.evaluate(ctx),
            self.hoistway.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("ahj-inspection-gate", ctx, gates, {
            "GO": "AHJ inspection path clear.",
            "HOLD": "AHJ inspection holding.",
            "ABORT": "AHJ inspection aborted.",
        })

    def weather_protect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.weather.evaluate(ctx),
            self.pit.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish("weather-protect-gate", ctx, gates, {
            "GO": "Weather/protection clear.",
            "HOLD": "Weather holding.",
            "ABORT": "Weather aborted.",
        })

    def elevator_turnover(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "ahj": {**(ctx.get("ahj") or {}), "required_for_turnover": True}}
        gates = [
            self.ahj.evaluate(ctx),
            self.turnover.evaluate(ctx),
            self.devices.evaluate(ctx),
            self.qa.evaluate(ctx, phase="closeout"),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("elevator-turnover", ctx, gates, {
            "GO": "Elevator turnover clear.",
            "HOLD": "Elevator turnover holding.",
            "ABORT": "Elevator turnover aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "elevators-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "superintendent")},
        )]
        summary = "ABORT escalated — stop work and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
