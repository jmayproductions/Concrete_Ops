"""Deterministic specialist gates for elevators / VTR."""

from __future__ import annotations

from typing import Any

from modules.elevators_swarm.schemas import GateResult

ERECT_ROLES = ('elevators_lead', 'mechanic', 'helper', 'electrician', 'adjuster', 'qc_tech', 'safety_watch')


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class EquipmentSubmittalAgent:
    name = "equipment-submittal"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("equipment") or {}
        miss = _missing(m, ("shops_approved", "machine_approved", "controller_approved"))
        if miss:
            return GateResult(self.name, "HOLD", "Equipment submittals incomplete: " + ", ".join(miss), {"equipment": m})
        return GateResult(self.name, "PASS", "Elevator equipment submittals clear", {"equipment": m})


class PitMachineRoomAgent:
    name = "pit-machine-room"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("pit_mr") or {}
        miss = _missing(p, ("pit_ready", "mr_ready", "power_ready"))
        if miss:
            return GateResult(self.name, "HOLD", "Pit/MR incomplete: " + ", ".join(miss), {"pit_mr": p})
        if p.get("waterproofing_ok") is False:
            return GateResult(self.name, "HOLD", "Pit waterproofing deficient", {"pit_mr": p})
        if p.get("hvac_ok") is False:
            return GateResult(self.name, "HOLD", "Machine room HVAC/environment not ready", {"pit_mr": p})
        return GateResult(self.name, "PASS", "Pit/machine room clear", {"pit_mr": p})


class RailPlumbAgent:
    name = "rail-plumb"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        r = ctx.get("rails") or {}
        if r.get("plumb_ok") is False:
            return GateResult(self.name, "HOLD", "Guide rails out of plumb/tolerance", {"rails": r})
        if r.get("brackets_ok") is False:
            return GateResult(self.name, "HOLD", "Rail brackets/anchorage incomplete", {"rails": r})
        if not r.get("joints_ok"):
            return GateResult(self.name, "HOLD", "Rail joints/fishplates incomplete", {"rails": r})
        return GateResult(self.name, "PASS", "Rail plumb/brackets clear", {"rails": r})


class HoistwayClearanceAgent:
    name = "hoistway-clearance"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        h = ctx.get("hoistway") or {}
        if h.get("clearances_ok") is False:
            return GateResult(self.name, "HOLD", "Hoistway running clearances deficient", {"hoistway": h})
        if h.get("projections"):
            return GateResult(self.name, "HOLD", "Unauthorized projections: " + ", ".join(h["projections"]), {"hoistway": h})
        if h.get("overhead_ok") is False:
            return GateResult(self.name, "HOLD", "Overhead/refuge clearance deficient", {"hoistway": h})
        return GateResult(self.name, "PASS", "Hoistway clearances clear", {"hoistway": h})


class DoorEntranceAgent:
    name = "door-entrance"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("entrances") or {}
        if d.get("plumb_set") is False:
            return GateResult(self.name, "HOLD", "Entrances/sills not plumb/set", {"entrances": d})
        if d.get("rated_unlabeled"):
            return GateResult(self.name, "HOLD", "Fire-rated entrances unlabeled", {"entrances": d})
        if d.get("binding"):
            return GateResult(self.name, "HOLD", "Door panels/operators binding", {"entrances": d})
        return GateResult(self.name, "PASS", "Door/entrances clear", {"entrances": d})


class CabInstallAgent:
    name = "cab-install"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("cab") or {}
        if c.get("platform_ok") is False:
            return GateResult(self.name, "HOLD", "Cab platform/sling not accepted", {"cab": c})
        if c.get("overweight"):
            return GateResult(self.name, "HOLD", "Cab finishes overweight vs design", {"cab": c})
        return GateResult(self.name, "PASS", "Cab install clear", {"cab": c})


class ElectricalControllerAgent:
    name = "electrical-controller"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("electrical") or {}
        miss = _missing(e, ("controller_set", "machine_set", "disconnects_labeled"))
        if miss:
            return GateResult(self.name, "HOLD", "Electrical/controls incomplete: " + ", ".join(miss), {"electrical": e})
        if e.get("grounded") is False:
            return GateResult(self.name, "HOLD", "Controller/machine grounding incomplete", {"electrical": e})
        return GateResult(self.name, "PASS", "Electrical/controller clear", {"electrical": e})


class SafetyDevicesAgent:
    name = "safety-devices"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("devices") or {}
        if s.get("bypassed"):
            return GateResult(self.name, "FAIL", "Safety devices bypassed", {"devices": s})
        miss = _missing(s, ("governor_ok", "safeties_ok", "buffers_ok", "interlocks_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Safety devices incomplete: " + ", ".join(miss), {"devices": s})
        return GateResult(self.name, "PASS", "Safety devices clear", {"devices": s})


class AhjInspectionAgent:
    name = "ahj-inspection"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("ahj") or {}
        if not a.get("permit_current"):
            return GateResult(self.name, "HOLD", "Installation permit not current", {"ahj": a})
        if a.get("passed") is False and not a.get("scheduled"):
            return GateResult(self.name, "HOLD", "AHJ/QEI inspection not passed or scheduled", {"ahj": a})
        if a.get("open_punch"):
            return GateResult(self.name, "HOLD", "AHJ punch open: " + ", ".join(a["open_punch"]), {"ahj": a})
        if a.get("required_for_turnover") and not a.get("passed"):
            return GateResult(self.name, "HOLD", "AHJ pass required before turnover", {"ahj": a})
        return GateResult(self.name, "PASS", "AHJ/inspection clear", {"ahj": a})


class TemporaryRunAgent:
    name = "temporary-run"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("temp_run") or {}
        if t.get("unauthorized") or t.get("public_use"):
            return GateResult(self.name, "FAIL", "Unauthorized temporary run / public exposure", {"temp_run": t})
        if not t.get("agreement"):
            return GateResult(self.name, "HOLD", "Temporary run agreement/controls missing", {"temp_run": t})
        if not t.get("qualified_operator"):
            return GateResult(self.name, "HOLD", "No qualified operator for temporary run", {"temp_run": t})
        if t.get("barricades_ok") is False:
            return GateResult(self.name, "HOLD", "Hoistway barricades/protection deficient", {"temp_run": t})
        return GateResult(self.name, "PASS", "Temporary run controls clear", {"temp_run": t})


class TurnoverTrainingAgent:
    name = "turnover-training"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("turnover") or {}
        miss = _missing(t, ("om_manuals", "keys_transferred", "training_complete"))
        if miss:
            return GateResult(self.name, "HOLD", "Turnover incomplete: " + ", ".join(miss), {"turnover": t})
        return GateResult(self.name, "PASS", "Turnover/training clear", {"turnover": t})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather/environment data", {})
        holds = []
        if w.get("hoistway_open") and not w.get("protected"):
            holds.append("open hoistway without weather protection")
        if w.get("mr_not_weathertight") and w.get("equipment_set"):
            holds.append("machine room not weathertight with equipment set")
        if w.get("freezing_hydraulics"):
            holds.append("freeze risk for hydraulic oil/system")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/protection CLEAR", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("hoistway") or {}).get("unprotected_opening"):
            violations.append("open hoistway without barricades/fall protection")
        if (ctx.get("devices") or {}).get("bypassed"):
            violations.append("safety devices bypassed")
        if (ctx.get("temp_run") or {}).get("unauthorized") or (ctx.get("temp_run") or {}).get("public_use"):
            violations.append("unauthorized temporary run / public exposure")
        if (ctx.get("suspended") or {}).get("no_secondary"):
            violations.append("work under suspended load without secondary protection")
        if (ctx.get("pit_entry") or {}).get("no_permit"):
            violations.append("confined pit entry without permit/attendant")
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
            return GateResult(self.name, "PASS", "Pre-elevator QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class ElevatorsLeadAgent:
    name = "elevators-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked elevator work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('car_id', 'car'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
