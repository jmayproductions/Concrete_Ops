"""Named earthwork workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.earthwork_swarm.agents import (
    CompactionAgent,
    CrewOpsAgent,
    DrainageSwalesAgent,
    EarthworkLeadAgent,
    ErosionControlAgent,
    ExcavationAgent,
    GeotechAgent,
    MaterialsFillAgent,
    PavingPrepAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SubgradeAgent,
    SurveyControlAgent,
    TrenchBackfillAgent,
    UtilitiesLocateAgent,
    WeatherProtectAgent,
)
from modules.earthwork_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-earthwork-gate",
    "utilities-locate-gate",
    "excavation-runbook",
    "subgrade-accept-gate",
    "compaction-lift-runbook",
    "trench-backfill-gate",
    "drainage-swale-qa",
    "erosion-control-gate",
    "paving-prep-gate",
    "weather-protect-gate",
    "earthwork-closeout",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next earthwork sequence / workflow", "Keep BMPs + density logs current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — secure trench/slopes; call utility owner if strike",
            "Preserve photos, dig ticket, density logs, timestamps",
            "Re-enter through pre-earthwork-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "earthwork-lead"]
    return [
        "Do not advance fill lifts / pave / trench cover",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.materials = MaterialsFillAgent()
        self.survey = SurveyControlAgent()
        self.utilities = UtilitiesLocateAgent()
        self.excavation = ExcavationAgent()
        self.subgrade = SubgradeAgent()
        self.compaction = CompactionAgent()
        self.trench = TrenchBackfillAgent()
        self.drainage = DrainageSwalesAgent()
        self.erosion = ErosionControlAgent()
        self.paving = PavingPrepAgent()
        self.weather = WeatherProtectAgent()
        self.geotech = GeotechAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = EarthworkLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_earthwork_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.materials.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.utilities.evaluate(ctx),
            self.erosion.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-earthwork-gate", ctx, gates, {
            "GO": "Pre-earthwork clear — grading/excavate sequence may proceed.",
            "HOLD": "Pre-earthwork holding — locate/BMPs/materials/weather.",
            "ABORT": "Pre-earthwork aborted by fail-safe.",
        })

    def utilities_locate_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.utilities.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("utilities-locate-gate", ctx, gates, {
            "GO": "Utility locate clear — dig may proceed in marked zone.",
            "HOLD": "Utility locate holding.",
            "ABORT": "Utility locate aborted — stop dig.",
        })

    def excavation_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.utilities.evaluate(ctx),
            self.excavation.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("excavation-runbook", ctx, gates, {
            "GO": "Excavation runbook clear.",
            "HOLD": "Excavation holding.",
            "ABORT": "Excavation aborted — secure trench/slopes.",
        })

    def subgrade_accept_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.subgrade.evaluate(ctx),
            self.geotech.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("subgrade-accept-gate", ctx, gates, {
            "GO": "Subgrade accepted — fill/pave section may proceed.",
            "HOLD": "Subgrade holding — soft spots or geotech.",
            "ABORT": "Subgrade aborted.",
        })

    def compaction_lift_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.materials.evaluate(ctx),
            self.compaction.evaluate(ctx),
            self.geotech.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("compaction-lift-runbook", ctx, gates, {
            "GO": "Compaction lift clear.",
            "HOLD": "Compaction holding — density/moisture/lift.",
            "ABORT": "Compaction aborted.",
        })

    def trench_backfill_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "require_trench": True}
        gates = [
            self.utilities.evaluate(ctx),
            self.trench.evaluate(ctx),
            self.compaction.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("trench-backfill-gate", ctx, gates, {
            "GO": "Trench backfill clear.",
            "HOLD": "Trench backfill holding.",
            "ABORT": "Trench backfill aborted.",
        })

    def drainage_swale_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.drainage.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.erosion.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("drainage-swale-qa", ctx, gates, {
            "GO": "Drainage/swale QA clear.",
            "HOLD": "Drainage holding.",
            "ABORT": "Drainage aborted.",
        })

    def erosion_control_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.erosion.evaluate(ctx),
            self.drainage.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("erosion-control-gate", ctx, gates, {
            "GO": "Erosion control clear for disturbance.",
            "HOLD": "Erosion control holding.",
            "ABORT": "Erosion control aborted.",
        })

    def paving_prep_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "require_paving": True}
        gates = [
            self.subgrade.evaluate(ctx),
            self.compaction.evaluate(ctx),
            self.paving.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("paving-prep-gate", ctx, gates, {
            "GO": "Paving prep clear — pave day may proceed.",
            "HOLD": "Paving prep holding.",
            "ABORT": "Paving prep aborted.",
        })

    def weather_protect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.weather.evaluate(ctx),
            self.erosion.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish("weather-protect-gate", ctx, gates, {
            "GO": "Weather/protection clear.",
            "HOLD": "Weather holding.",
            "ABORT": "Weather aborted.",
        })

    def earthwork_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "require_paving": True}
        gates = [
            self.qa.evaluate(ctx, phase="closeout"),
            self.survey.evaluate(ctx),
            self.drainage.evaluate(ctx),
            self.erosion.evaluate(ctx),
            self.paving.evaluate(ctx),
            self.geotech.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("earthwork-closeout", ctx, gates, {
            "GO": "Earthwork closeout clear.",
            "HOLD": "Earthwork closeout holding.",
            "ABORT": "Earthwork closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "earthwork-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "superintendent")},
        )]
        summary = "ABORT escalated — stop work and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
