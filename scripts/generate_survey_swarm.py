#!/usr/bin/env python3
"""Generate survey / layout / control field swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("survey-lead", "SurveyLead", "Owns survey sequence and final GO/HOLD/ABORT.",
     """You own **survey / layout / control** sequencing and assemble GO/HOLD/ABORT.

## Sequence pattern
1. Control network + benchmarks verified / calibrated equipment
2. Stake-out from approved drawings/BIM
3. Embeds/anchors/grid lines set before trade cover
4. Grade checks vs design; tolerances logged
5. As-builts captured; deviations dispositioned
6. Closeout package for AHJ / turnover

Do not invent coordinates, elevations, or tolerance values."""),
    ("control-network", "ControlNetwork", "Owns primary/secondary control and traverse closure.",
     """You own site control network.

## Checks
- Primary control established and protected
- Traverse/network closure within project tolerance
- Transformations / site calibrations documented

HOLD stake-out on unverified or disturbed primary control."""),
    ("benchmarks", "Benchmarks", "Owns vertical benchmarks and datum.",
     """You own vertical control.

## Checks
- Benchmarks tied to project datum
- BM stability verified (not heaved/disturbed)
- Temporary BMs documented and checked

HOLD grade work without verified BM."""),
    ("stakeout", "Stakeout", "Owns horizontal stake-out of grids, lines, and points.",
     """You own stake-out.

## Checks
- Stakes from approved revision / model
- Offsets and cut sheets issued to trades
- Disturbed stakes re-set before work

HOLD work to missing or outdated stakes."""),
    ("as-built", "AsBuilt", "Owns as-built capture and deviation logs.",
     """You own as-builts.

## Checks
- Critical elements captured before cover
- Deviations logged with element IDs
- Files delivered in required format (CAD/CSV/IFC)

HOLD cover when required as-builts not captured."""),
    ("tolerance-check", "ToleranceCheck", "Owns geometric tolerance acceptance.",
     """You own tolerance checks.

## Checks
- Measured vs allowable (plan/elevation/plumb)
- Out-of-tolerance flagged for eng/trade rework
- Acceptance recorded before next trade

HOLD advancing work beyond failed tolerances."""),
    ("bim-layout", "BimLayout", "Owns model-based layout and clash with field.",
     """You own BIM / model layout.

## Checks
- Model revision locked for layout session
- Field-to-model discrepancies logged
- Layout points published from approved federated model

HOLD layout from superseded model revision."""),
    ("embeds-anchor-layout", "EmbedsAnchorLayout", "Owns embed, anchor, and sleeve layout.",
     """You own embeds/anchors layout.

## Checks
- Embed/anchor/sleeve locations staked before pour/cover
- Elevations and orientations checked
- Conflicts with rebar/MEP resolved

HOLD pour/cover with missing embed layout."""),
    ("grade-checking", "GradeChecking", "Owns finish grade and subgrade elevation checks.",
     """You own grade checking.

## Checks
- Spot elevations vs design surface
- Blue tops / hubs for paving/grade
- Drainage slopes confirmed (no reverse grade)

HOLD pave/pour on unverified grade."""),
    ("monitoring-settlement", "MonitoringSettlement", "Owns settlement/deformation survey when required.",
     """You own deformation monitoring.

## Checks
- Baseline points established before excavate/load
- Readings on frequency; alarms reported
- Triggers escalate to eng/SOE

HOLD ignoring required monitoring cycle."""),
    ("equipment-calibration", "EquipmentCalibration", "Owns instrument calibration and field checks.",
     """You own survey equipment readiness.

## Checks
- Total station/GNSS/level calibration current
- Field calibration / collimation checks done
- Batteries/targets adequate for shift

HOLD layout with overdue calibration."""),
    ("utility-locate-coord", "UtilityLocateCoord", "Owns coordination with dig tickets before stake/dig.",
     """You own utility awareness for survey ops.

## Checks
- Dig ticket status known when staking near excavation
- Marks preserved; conflicts flagged to GC
- Soft-dig notes on cut sheets when required

HOLD aggressive dig stake-out over unmarked utilities."""),
    ("weather-protect", "WeatherProtect", "Owns visibility and atmospheric survey holds.",
     """You own weather holds for survey.

## Holds
- Fog/rain/heat shimmer preventing reliable observations
- High wind affecting prism/rod stability when critical
- Lightning for outdoor instrument work

HOLD critical layout in unusable conditions."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work for open edges, traffic, and destroyed control.",
     """You have stop-work authority. FAIL => swarm **ABORT**.

## Fail conditions
- Surveying at unprotected open edges / hoistways
- Primary control destroyed and work continuing without re-establish
- Layout crew in live traffic without controls
- Digging to stakes across unmarked live utilities"""),
    ("crew-ops", "CrewOps", "Owns party roles, briefing, and fatigue.",
     """You own survey party readiness.

## Roles
survey_lead, instrument_op, rod_person, cad_tech, qc_tech, safety_watch, gc_coordinator

HOLD missing roles, incomplete briefing, or fatigue risk."""),
    ("qa-inspector", "QaInspector", "Owns survey records and hold-point evidence.",
     """You own survey QA evidence.

## Checks
- Control / stake / as-built records filed
- Tolerance sheets signed
- NCRs for out-of-tolerance dispositioned

HOLD missing survey documentation for claimed release."""),
]

WORKFLOWS = [
    "pre-survey-gate",
    "control-network-gate",
    "stakeout-runbook",
    "embed-layout-gate",
    "grade-check-gate",
    "as-built-capture",
    "tolerance-accept-gate",
    "bim-layout-gate",
    "calibration-gate",
    "weather-protect-gate",
    "survey-closeout",
    "hold-abort",
]

ROLES = (
    "survey_lead",
    "instrument_op",
    "rod_person",
    "cad_tech",
    "qc_tech",
    "safety_watch",
    "gc_coordinator",
)

ORDERS = {
    "pre-survey-gate": ["equipment-calibration", "control-network", "benchmarks", "crew-ops", "weather-protect", "safety-failsafe", "qa-inspector"],
    "control-network-gate": ["control-network", "benchmarks", "equipment-calibration", "qa-inspector"],
    "stakeout-runbook": ["control-network", "stakeout", "bim-layout", "utility-locate-coord", "qa-inspector", "safety-failsafe"],
    "embed-layout-gate": ["embeds-anchor-layout", "stakeout", "tolerance-check", "qa-inspector", "safety-failsafe"],
    "grade-check-gate": ["grade-checking", "benchmarks", "tolerance-check", "qa-inspector"],
    "as-built-capture": ["as-built", "tolerance-check", "qa-inspector"],
    "tolerance-accept-gate": ["tolerance-check", "as-built", "qa-inspector", "safety-failsafe"],
    "bim-layout-gate": ["bim-layout", "stakeout", "equipment-calibration", "qa-inspector"],
    "calibration-gate": ["equipment-calibration", "control-network", "qa-inspector"],
    "weather-protect-gate": ["weather-protect", "safety-failsafe"],
    "survey-closeout": ["qa-inspector", "as-built", "control-network", "tolerance-check", "crew-ops"],
    "hold-abort": [],
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content)


def child_mcs(folder: str, description: str, instructions: str) -> str:
    return f"""kind: AgentDialog

beginDialog:
  kind: OnToolSelected
  id: main
  description: {description}

settings:
  instructions: |
    # {folder} Specialist

{textwrap.indent(instructions.strip(), '    ')}

    ## Copilot Studio output contract
    Return structured outputs only to the parent — do not reply to the field user directly.
    Decision: GO | HOLD | ABORT. Prefer SurveyContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: SurveyContextJson
    description: JSON context for survey control stakeout as-built tolerances
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    SurveyContextJson:
      displayName: Survey Context JSON
      description: JSON context for survey / layout / control
      type: String
    WorkflowId:
      displayName: Workflow Id
      description: Named workflow id
      type: String

outputType:
  properties:
    Decision:
      displayName: Decision
      description: GO, HOLD, or ABORT
      type: String
    Summary:
      displayName: Summary
      description: Short field-facing summary
      type: String
    GatesJson:
      displayName: GatesJson
      description: JSON array of gate results
      type: String
    ActionsJson:
      displayName: ActionsJson
      description: JSON array of next field actions
      type: String
"""


def main() -> None:
    agents_root = ROOT / "agents" / "survey"
    studio = ROOT / "copilot-studio" / "survey-crew"
    mod = ROOT / "modules" / "survey_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for Survey / Layout / Control Swarm

From project `construction.md` extractions and typical field survey ITP practice:

- Control network, benchmarks, and equipment calibration
- Stake-out, embed/anchor layout, grade checking
- As-built capture and geometric tolerance acceptance before cover
""")
    write(agents_root / "README.md", """# Survey / Layout / Control Swarm (reference twin)

> See [`../../copilot-studio/survey-crew/`](../../copilot-studio/survey-crew/) → `START_HERE.md`.

```bash
python -m modules.survey_swarm.cli list
python -m modules.survey_swarm.cli run pre-survey-gate -c agents/survey/fixtures/pre_survey_go.yaml
python -m modules.survey_swarm.api --port 8094
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# Survey Swarm — Coordinator

Return one GO / HOLD / ABORT for survey / layout / control.

## Hard rules
1. No stake-out on unverified or destroyed primary control.
2. Equipment calibration current before critical layout.
3. Embeds/grades checked before pour/pave/cover.
4. As-builts captured when required before concealment.
5. SafetyFailsafe FAIL → ABORT.
"""
    write(agents_root / "instructions" / "root.md", root)
    write(studio / "knowledge" / "files" / "root.md", root)
    write(studio / "knowledge" / "files" / "SOURCES.md", (agents_root / "SOURCES.md").read_text())

    for wid in WORKFLOWS:
        order = ORDERS[wid]
        body = f"# Workflow: `{wid}`\n\nGate order:\n"
        body += ("\n".join(f"{i+1}. `{a}`" for i, a in enumerate(order)) + "\n") if order else "Escalation only.\n"
        body += "\nSafetyFailsafe FAIL => ABORT.\n"
        write(agents_root / "workflows" / f"{wid}.md", body)
        write(studio / "knowledge" / "files" / f"{wid}.md", body)

    children = ", ".join(s[1] for s in SPECIALISTS)
    write(studio / "agent.mcs.yml", f"""mcs.metadata:
  componentName: SurveyLayoutSwarm
kind: GptComponentMetadata
displayName: Survey Layout Swarm
instructions: |
  You are the Survey / Layout / Control Swarm coordinator.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect SurveyContextJson; missing critical fields => HOLD (do not invent readings).
  3. Invoke child agents IN DOCUMENTED ORDER for that workflow.
  4. Wait for Decision/Summary/GatesJson/ActionsJson from each child.
  5. One parent reply only. Children must not reply to the field user.
  6. SafetyFailsafe FAIL => final Decision ABORT.

  ## Output shape
  WORKFLOW: <id>
  DECISION: GO | HOLD | ABORT
  SUMMARY: <2-4 sentences>
  GATES:
  - <agent>: PASS|FAIL|HOLD — <one line>
  ACTIONS:
  - <next field action>

  ## Workflow catalog
  {", ".join(WORKFLOWS)}.

conversationStarters:
  - title: Pre-survey gate
    text: Run pre-survey-gate for Site Control and return GO/HOLD/ABORT.
  - title: Stake-out
    text: Run stakeout-runbook for Grid A–D Level 2.
  - title: Embed layout
    text: Run embed-layout-gate before Deck L3 pour.
  - title: Grade check
    text: Run grade-check-gate for parking lot subgrade.
  - title: As-built capture
    text: Run as-built-capture for underground utilities.
  - title: Tolerance accept
    text: Run tolerance-accept-gate for column line deviation.

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: Survey Layout Swarm
schemaName: survey_layout_swarm
accessControlPolicy: ChatbotReaders
authenticationMode: Integrated
configuration:
  settings:
    GenerativeActionsEnabled: true
  recognizer:
    kind: GenerativeAIRecognizer
language: 1033
""")
    write(studio / "connectionreferences.mcs.yml", "# Populated by Copilot Studio when connectors/MCP are bound.\n[]\n")
    write(studio / ".vscode" / "extensions.json", '{\n  "recommendations": ["microsoft-IsvExpTools.powerplatform-vscode", "microsoft.copilotstudio-vscode", "redhat.vscode-yaml"]\n}\n')
    write(studio / "topics" / "Greeting.topic.mcs.yml", """kind: AdaptiveDialog
beginDialog:
  kind: OnConversationStart
  id: main
  actions:
    - kind: SendActivity
      id: sendGreeting
      activity:
        text:
          - Survey Layout Swarm ready. Ask for pre-survey-gate, stakeout-runbook, embed-layout-gate, grade-check-gate, as-built-capture, or another named workflow. I return GO / HOLD / ABORT.
          - Survey online — share area/control context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.survey_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for survey / layout / control QA gates.\n")
    write(studio / "START_HERE.md", """# START HERE — Survey Layout Swarm drop-in

Ready Copilot Studio workspace for survey / layout / control field gates.

## 3 steps
1. Open this `survey-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Survey Layout Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-survey-gate…”*.

## Workflows
`pre-survey-gate`, `control-network-gate`, `stakeout-runbook`, `embed-layout-gate`, `grade-check-gate`, `as-built-capture`, `tolerance-accept-gate`, `bim-layout-gate`, `calibration-gate`, `weather-protect-gate`, `survey-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.survey_swarm.api --port 8094
python -m modules.survey_swarm.cli run pre-survey-gate -c agents/survey/fixtures/pre_survey_go.yaml
```
""")

    write(mod / "schemas.py", """from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

GateStatus = Literal["PASS", "FAIL", "HOLD", "ADVISORY", "SKIP"]
Decision = Literal["GO", "HOLD", "ABORT"]


@dataclass
class GateResult:
    agent: str
    status: GateStatus
    detail: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SwarmResult:
    workflow: str
    zone_id: str
    decision: Decision
    summary: str
    gates: list[GateResult]
    actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow,
            "zone_id": self.zone_id,
            "decision": self.decision,
            "summary": self.summary,
            "gates": [g.to_dict() for g in self.gates],
            "actions": list(self.actions),
        }

    def render(self) -> str:
        lines = [
            f"WORKFLOW: {self.workflow}",
            f"ZONE: {self.zone_id}",
            f"DECISION: {self.decision}",
            f"SUMMARY: {self.summary}",
            "GATES:",
        ]
        for g in self.gates:
            lines.append(f"- {g.agent}: {g.status} — {g.detail}")
        lines.append("ACTIONS:")
        for a in self.actions:
            lines.append(f"- {a}")
        return chr(10).join(lines)
""")

    agents_src = r'''"""Deterministic specialist gates for survey / layout / control."""

from __future__ import annotations

from typing import Any

from modules.survey_swarm.schemas import GateResult

ERECT_ROLES = __ROLES__


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class ControlNetworkAgent:
    name = "control-network"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("control") or {}
        if c.get("destroyed") and not c.get("reestablished"):
            return GateResult(self.name, "FAIL", "Primary control destroyed — re-establish before work", {"control": c})
        if not c.get("verified"):
            return GateResult(self.name, "HOLD", "Control network not verified", {"control": c})
        if c.get("closure_ok") is False:
            return GateResult(self.name, "HOLD", "Traverse/network closure out of tolerance", {"control": c})
        return GateResult(self.name, "PASS", "Control network clear", {"control": c})


class BenchmarksAgent:
    name = "benchmarks"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("benchmarks") or {}
        if not b.get("datum_tied"):
            return GateResult(self.name, "HOLD", "Benchmarks not tied to project datum", {"benchmarks": b})
        if b.get("disturbed"):
            return GateResult(self.name, "HOLD", "Benchmarks disturbed/heaved — re-verify", {"benchmarks": b})
        return GateResult(self.name, "PASS", "Benchmarks clear", {"benchmarks": b})


class StakeoutAgent:
    name = "stakeout"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("stakeout") or {}
        if not s.get("from_approved_rev"):
            return GateResult(self.name, "HOLD", "Stake-out not from approved revision/model", {"stakeout": s})
        if s.get("stakes_missing"):
            return GateResult(self.name, "HOLD", "Missing/disturbed stakes: " + ", ".join(s["stakes_missing"]), {"stakeout": s})
        if not s.get("cut_sheets_issued"):
            return GateResult(self.name, "HOLD", "Cut sheets not issued to trades", {"stakeout": s})
        return GateResult(self.name, "PASS", "Stake-out clear", {"stakeout": s})


class AsBuiltAgent:
    name = "as-built"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("asbuilt") or {}
        if a.get("required") is False:
            return GateResult(self.name, "PASS", "As-built not required this gate", {"asbuilt": a})
        if not a.get("captured"):
            return GateResult(self.name, "HOLD", "Required as-builts not captured before cover", {"asbuilt": a})
        if a.get("format_ok") is False:
            return GateResult(self.name, "HOLD", "As-built deliverable format incomplete", {"asbuilt": a})
        return GateResult(self.name, "PASS", "As-built capture clear", {"asbuilt": a})


class ToleranceCheckAgent:
    name = "tolerance-check"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("tolerance") or {}
        if t.get("within_tolerance") is False:
            return GateResult(self.name, "HOLD", f"Out of tolerance: {t.get('notes', 'see field book')}", {"tolerance": t})
        if not t.get("checked"):
            return GateResult(self.name, "HOLD", "Tolerance checks not recorded", {"tolerance": t})
        return GateResult(self.name, "PASS", "Tolerance checks clear", {"tolerance": t})


class BimLayoutAgent:
    name = "bim-layout"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bim") or {}
        if b.get("required") is False:
            return GateResult(self.name, "SKIP", "No BIM layout this gate", {})
        if b.get("superseded_model"):
            return GateResult(self.name, "HOLD", "Layout from superseded model revision", {"bim": b})
        if not b.get("revision_locked"):
            return GateResult(self.name, "HOLD", "Model revision not locked for layout", {"bim": b})
        return GateResult(self.name, "PASS", "BIM layout clear", {"bim": b})


class EmbedsAnchorLayoutAgent:
    name = "embeds-anchor-layout"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("embeds") or {}
        if e.get("required") is False:
            return GateResult(self.name, "SKIP", "No embeds layout this gate", {})
        if e.get("missing"):
            return GateResult(self.name, "HOLD", "Embeds/anchors not laid out: " + ", ".join(e["missing"]), {"embeds": e})
        if e.get("conflicts"):
            return GateResult(self.name, "HOLD", "Embed conflicts: " + ", ".join(e["conflicts"]), {"embeds": e})
        return GateResult(self.name, "PASS", "Embeds/anchor layout clear", {"embeds": e})


class GradeCheckingAgent:
    name = "grade-checking"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("grade") or {}
        if g.get("verified") is False:
            return GateResult(self.name, "HOLD", "Grade not verified vs design", {"grade": g})
        if g.get("reverse_slope"):
            return GateResult(self.name, "HOLD", "Reverse drainage slope detected", {"grade": g})
        return GateResult(self.name, "PASS", "Grade checking clear", {"grade": g})


class MonitoringSettlementAgent:
    name = "monitoring-settlement"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("monitoring") or {}
        if m.get("required") is False:
            return GateResult(self.name, "SKIP", "No deformation monitoring", {})
        if not m.get("baseline_set"):
            return GateResult(self.name, "HOLD", "Monitoring baseline not set", {"monitoring": m})
        if m.get("readings_current") is False:
            return GateResult(self.name, "HOLD", "Monitoring readings overdue", {"monitoring": m})
        if m.get("alarm"):
            return GateResult(self.name, "HOLD", "Monitoring alarm — eng review", {"monitoring": m})
        return GateResult(self.name, "PASS", "Settlement monitoring clear", {"monitoring": m})


class EquipmentCalibrationAgent:
    name = "equipment-calibration"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("equipment") or {}
        if e.get("calibration_current") is False:
            return GateResult(self.name, "HOLD", "Instrument calibration overdue", {"equipment": e})
        if e.get("field_check_ok") is False:
            return GateResult(self.name, "HOLD", "Field collimation/calibration check failed", {"equipment": e})
        return GateResult(self.name, "PASS", "Equipment calibration clear", {"equipment": e})


class UtilityLocateCoordAgent:
    name = "utility-locate-coord"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        u = ctx.get("utilities") or {}
        if u.get("required") is False:
            return GateResult(self.name, "PASS", "No dig/utility coordination this gate", {"utilities": u})
        if u.get("dig_without_locate"):
            return GateResult(self.name, "FAIL", "Stake/dig path without utility locate", {"utilities": u})
        if not u.get("ticket_known"):
            return GateResult(self.name, "HOLD", "Dig ticket status unknown for stake area", {"utilities": u})
        return GateResult(self.name, "PASS", "Utility locate coordination clear", {"utilities": u})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather/visibility data", {})
        holds = []
        if w.get("poor_visibility"):
            holds.append("fog/rain/shimmer — observations unreliable")
        if w.get("high_wind_critical"):
            holds.append("high wind affecting critical observations")
        if w.get("lightning"):
            holds.append("lightning — outdoor instrument hold")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/visibility CLEAR", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("edge") or {}).get("unprotected"):
            violations.append("surveying at unprotected open edge")
        if (ctx.get("control") or {}).get("destroyed") and not (ctx.get("control") or {}).get("reestablished"):
            violations.append("primary control destroyed — work continuing")
        if (ctx.get("traffic") or {}).get("uncontrolled"):
            violations.append("layout crew in live traffic without controls")
        if (ctx.get("utilities") or {}).get("dig_without_locate"):
            violations.append("dig/stake across unmarked utilities")
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
        return GateResult(self.name, "PASS", f"Party ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-survey QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} survey docs clear", {})
        return GateResult(self.name, "HOLD", f"No survey QA evidence for phase={phase}", {"qa": q})


class SurveyLeadAgent:
    name = "survey-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked survey/layout work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named survey / layout workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.survey_swarm.agents import (
    AsBuiltAgent,
    BenchmarksAgent,
    BimLayoutAgent,
    ControlNetworkAgent,
    CrewOpsAgent,
    EmbedsAnchorLayoutAgent,
    EquipmentCalibrationAgent,
    GradeCheckingAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    StakeoutAgent,
    SurveyLeadAgent,
    ToleranceCheckAgent,
    UtilityLocateCoordAgent,
    WeatherProtectAgent,
)
from modules.survey_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-survey-gate",
    "control-network-gate",
    "stakeout-runbook",
    "embed-layout-gate",
    "grade-check-gate",
    "as-built-capture",
    "tolerance-accept-gate",
    "bim-layout-gate",
    "calibration-gate",
    "weather-protect-gate",
    "survey-closeout",
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
        return ["Proceed to next survey/layout sequence", "Protect control + file cut sheets/as-builts"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — re-establish control; clear edge/traffic/utility hazards",
            "Preserve field books, coordinates, photos, timestamps",
            "Re-enter through pre-survey-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "survey-lead"]
    return [
        "Do not pour / pave / cover to unverified layout",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.control = ControlNetworkAgent()
        self.benchmarks = BenchmarksAgent()
        self.stakeout = StakeoutAgent()
        self.asbuilt = AsBuiltAgent()
        self.tolerance = ToleranceCheckAgent()
        self.bim = BimLayoutAgent()
        self.embeds = EmbedsAnchorLayoutAgent()
        self.grade = GradeCheckingAgent()
        self.equipment = EquipmentCalibrationAgent()
        self.utilities = UtilityLocateCoordAgent()
        self.weather = WeatherProtectAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = SurveyLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_survey_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.equipment.evaluate(ctx),
            self.control.evaluate(ctx),
            self.benchmarks.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-survey-gate", ctx, gates, {
            "GO": "Pre-survey clear — layout may proceed.",
            "HOLD": "Pre-survey holding — control/calibration/weather.",
            "ABORT": "Pre-survey aborted by fail-safe.",
        })

    def control_network_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.control.evaluate(ctx),
            self.benchmarks.evaluate(ctx),
            self.equipment.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("control-network-gate", ctx, gates, {
            "GO": "Control network clear.",
            "HOLD": "Control network holding.",
            "ABORT": "Control network aborted.",
        })

    def stakeout_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.control.evaluate(ctx),
            self.stakeout.evaluate(ctx),
            self.bim.evaluate(ctx),
            self.utilities.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("stakeout-runbook", ctx, gates, {
            "GO": "Stake-out clear.",
            "HOLD": "Stake-out holding.",
            "ABORT": "Stake-out aborted.",
        })

    def embed_layout_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "embeds": {**(ctx.get("embeds") or {}), "required": True}}
        gates = [
            self.embeds.evaluate(ctx),
            self.stakeout.evaluate(ctx),
            self.tolerance.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("embed-layout-gate", ctx, gates, {
            "GO": "Embed/anchor layout clear.",
            "HOLD": "Embed layout holding.",
            "ABORT": "Embed layout aborted.",
        })

    def grade_check_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.grade.evaluate(ctx),
            self.benchmarks.evaluate(ctx),
            self.tolerance.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("grade-check-gate", ctx, gates, {
            "GO": "Grade check clear.",
            "HOLD": "Grade check holding.",
            "ABORT": "Grade check aborted.",
        })

    def as_built_capture(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "asbuilt": {**(ctx.get("asbuilt") or {}), "required": True}}
        gates = [
            self.asbuilt.evaluate(ctx),
            self.tolerance.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("as-built-capture", ctx, gates, {
            "GO": "As-built capture clear.",
            "HOLD": "As-built capture holding.",
            "ABORT": "As-built capture aborted.",
        })

    def tolerance_accept_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.tolerance.evaluate(ctx),
            self.asbuilt.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("tolerance-accept-gate", ctx, gates, {
            "GO": "Tolerance acceptance clear.",
            "HOLD": "Tolerance acceptance holding.",
            "ABORT": "Tolerance acceptance aborted.",
        })

    def bim_layout_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "bim": {**(ctx.get("bim") or {}), "required": True}}
        gates = [
            self.bim.evaluate(ctx),
            self.stakeout.evaluate(ctx),
            self.equipment.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("bim-layout-gate", ctx, gates, {
            "GO": "BIM layout clear.",
            "HOLD": "BIM layout holding.",
            "ABORT": "BIM layout aborted.",
        })

    def calibration_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.equipment.evaluate(ctx),
            self.control.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("calibration-gate", ctx, gates, {
            "GO": "Calibration clear.",
            "HOLD": "Calibration holding.",
            "ABORT": "Calibration aborted.",
        })

    def weather_protect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-protect-gate", ctx, gates, {
            "GO": "Weather/visibility clear.",
            "HOLD": "Weather holding.",
            "ABORT": "Weather aborted.",
        })

    def survey_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "asbuilt": {**(ctx.get("asbuilt") or {}), "required": True}}
        gates = [
            self.qa.evaluate(ctx, phase="closeout"),
            self.asbuilt.evaluate(ctx),
            self.control.evaluate(ctx),
            self.tolerance.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("survey-closeout", ctx, gates, {
            "GO": "Survey closeout clear.",
            "HOLD": "Survey closeout holding.",
            "ABORT": "Survey closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "survey-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "chief_of_parties")},
        )]
        summary = "ABORT escalated — stop work and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
''')

    write(mod / "swarm.py", '''"""Survey / layout swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.survey_swarm.schemas import SwarmResult
from modules.survey_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class SurveySwarm:
    def __init__(self, runner: WorkflowRunner | None = None) -> None:
        self.runner = runner or WorkflowRunner()
        self.handlers = get_workflow_handlers(self.runner)

    def list_workflows(self) -> list[str]:
        return list(WORKFLOW_IDS)

    def run(self, workflow: str, context: dict[str, Any] | None = None) -> SwarmResult:
        if workflow not in self.handlers:
            raise ValueError(f"Unknown workflow '{workflow}'. Known: {', '.join(WORKFLOW_IDS)}")
        ctx = dict(context or {})
        ctx.setdefault("zone_id", "ZONE-UNSET")
        log_event(f"[survey-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[survey-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["SurveySwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.survey_swarm.swarm import SurveySwarm, SwarmResult
from modules.survey_swarm.workflows import WORKFLOW_IDS

__all__ = ["SurveySwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for survey / layout swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.survey_swarm.swarm import SurveySwarm

app = typer.Typer(add_completion=False, help="Survey / layout / control field swarm")


def _load(path: Optional[Path]) -> dict:
    if path is None:
        return {}
    text = path.read_text()
    data = yaml.safe_load(text) if path.suffix.lower() in {".yaml", ".yml"} else json.loads(text)
    if not isinstance(data, dict):
        raise typer.BadParameter("Context must be an object")
    return data


@app.command("list")
def list_workflows() -> None:
    for w in SurveySwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = SurveySwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "survey" / "fixtures" / "pre_survey_go.yaml"
    result = SurveySwarm().run("pre-survey-gate", yaml.safe_load(fixture.read_text()))
    print(result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


if __name__ == "__main__":
    app()
''')
    write(mod / "api.py", '''"""HTTP API for Copilot Studio connectors."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from modules.survey_swarm.swarm import SurveySwarm
from modules.survey_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = SurveySwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[survey-swarm-api] {self.address_string()} {fmt % args}")

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        if path in ("/v1/workflows", "/v1/workflows/"):
            self._send(200, {"workflows": list(WORKFLOW_IDS)})
            return
        if path in ("/health", "/v1/health"):
            self._send(200, {"ok": True})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        prefix = "/v1/workflows/"
        if not path.startswith(prefix) or not path.endswith("/run"):
            self._send(404, {"error": "not found"})
            return
        workflow_id = unquote(path[len(prefix):-len("/run")].strip("/"))
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send(400, {"error": "invalid JSON"})
            return
        context = payload.get("context") or {}
        if isinstance(payload.get("SurveyContextJson"), str):
            try:
                context = {**context, **json.loads(payload["SurveyContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "SurveyContextJson is not valid JSON"})
                return
        try:
            result = self.swarm.run(workflow_id, context)
        except ValueError as exc:
            self._send(400, {"error": str(exc)})
            return
        self._send(200, result.to_dict())


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8094)
    args = p.parse_args()
    print(f"Survey layout swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-SITE-CONTROL
area: Site primary control
control:
  verified: true
  closure_ok: true
  destroyed: false
  reestablished: true
benchmarks:
  datum_tied: true
  disturbed: false
stakeout:
  from_approved_rev: true
  stakes_missing: []
  cut_sheets_issued: true
asbuilt:
  required: true
  captured: true
  format_ok: true
tolerance:
  checked: true
  within_tolerance: true
bim:
  required: true
  revision_locked: true
  superseded_model: false
embeds:
  required: true
  missing: []
  conflicts: []
grade:
  verified: true
  reverse_slope: false
equipment:
  calibration_current: true
  field_check_ok: true
utilities:
  required: true
  ticket_known: true
  dig_without_locate: false
weather:
  poor_visibility: false
  high_wind_critical: false
  lightning: false
crew:
  roles:
    - survey_lead
    - instrument_op
    - rod_person
    - cad_tech
    - qc_tech
    - safety_watch
    - gc_coordinator
  headcount: 7
  briefing_complete: true
  fatigued_workers: []
qa:
  pre_hold_points_clear: true
  install_hold_points_clear: true
edge:
  unprotected: false
traffic:
  uncontrolled: false
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_survey_go.yaml", go)
    write(studio / "samples" / "pre_survey_go.yaml", go)
    write(agents_root / "fixtures" / "control_destroyed_abort.yaml", """zone_id: DEMO-SITE-CONTROL
control:
  verified: false
  closure_ok: false
  destroyed: true
  reestablished: false
stakeout:
  from_approved_rev: true
  cut_sheets_issued: true
bim:
  required: false
utilities:
  required: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "out_of_tolerance_hold.yaml", """zone_id: DEMO-GRID-A
tolerance:
  checked: true
  within_tolerance: false
  notes: column line 0.75in off
asbuilt:
  required: true
  captured: true
  format_ok: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "superseded_bim_hold.yaml", """zone_id: DEMO-L2-GRIDS
bim:
  required: true
  revision_locked: false
  superseded_model: true
stakeout:
  from_approved_rev: false
  stakes_missing: [A-3, B-3]
  cut_sheets_issued: false
equipment:
  calibration_current: true
  field_check_ok: true
qa:
  install_hold_points_clear: true
""")
    write(agents_root / "fixtures" / "open_edge_abort.yaml", """zone_id: DEMO-DECK-EDGE
edge:
  unprotected: true
control:
  verified: true
  closure_ok: true
  destroyed: false
stakeout:
  from_approved_rev: true
  cut_sheets_issued: true
bim:
  required: false
utilities:
  required: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "calibration_hold.yaml", """zone_id: DEMO-SITE-CONTROL
equipment:
  calibration_current: false
  field_check_ok: false
control:
  verified: true
  closure_ok: true
  destroyed: false
benchmarks:
  datum_tied: true
  disturbed: false
weather:
  poor_visibility: false
crew:
  roles: [survey_lead, instrument_op, rod_person, cad_tech, qc_tech, safety_watch, gc_coordinator]
  briefing_complete: true
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")

    write(ROOT / "tests" / "test_survey_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.survey_swarm.swarm import SurveySwarm
from modules.survey_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "survey" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(SurveySwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_survey_go():
    assert SurveySwarm().run("pre-survey-gate", _load("pre_survey_go.yaml")).decision == "GO"


def test_control_destroyed_abort():
    assert SurveySwarm().run("stakeout-runbook", _load("control_destroyed_abort.yaml")).decision == "ABORT"


def test_out_of_tolerance_hold():
    assert SurveySwarm().run("tolerance-accept-gate", _load("out_of_tolerance_hold.yaml")).decision == "HOLD"


def test_superseded_bim_hold():
    assert SurveySwarm().run("bim-layout-gate", _load("superseded_bim_hold.yaml")).decision == "HOLD"


def test_open_edge_abort():
    assert SurveySwarm().run("stakeout-runbook", _load("open_edge_abort.yaml")).decision == "ABORT"


def test_calibration_hold():
    assert SurveySwarm().run("pre-survey-gate", _load("calibration_hold.yaml")).decision == "HOLD"


def test_embed_go():
    assert SurveySwarm().run("embed-layout-gate", _load("pre_survey_go.yaml")).decision == "GO"


def test_closeout_go():
    assert SurveySwarm().run("survey-closeout", _load("pre_survey_go.yaml")).decision == "GO"


def test_hold_abort():
    assert SurveySwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "control"}).decision == "ABORT"
''')

    gitattributes = ROOT / ".gitattributes"
    text = gitattributes.read_text() if gitattributes.exists() else ""
    if "*.zip binary" not in text:
        if not text.endswith("\n"):
            text += "\n"
        text += "\n*.zip binary\npackages/**/*.zip binary\n"
        gitattributes.write_text(text)

    readme = ROOT / "README.md"
    if readme.exists():
        rtxt = readme.read_text()
        marker = "Workflows: pour, PT, tilt-up, SOG, shotcrete, CIP walls, elevated deck / strip-reshore, mass thermal, curing lifecycle.\n"
        block = """Workflows: pour, PT, tilt-up, SOG, shotcrete, CIP walls, elevated deck / strip-reshore, mass thermal, curing lifecycle.

### Survey / Layout / Control Swarm (Copilot Studio)

Same pattern — field GO/HOLD/ABORT for control, stake-out, embeds, and as-builts:

- [`copilot-studio/survey-crew/`](copilot-studio/survey-crew/) — parent + 16 child agents; open `START_HERE.md`
- Drop-in zip: [`packages/SurveyLayout-Swarm-CopilotStudio-DropIn.zip`](packages/SurveyLayout-Swarm-CopilotStudio-DropIn.zip)

```bash
python -m modules.survey_swarm.api --port 8094
python -m modules.survey_swarm.cli run pre-survey-gate -c agents/survey/fixtures/pre_survey_go.yaml
```
"""
        if "Survey / Layout / Control Swarm" not in rtxt and marker in rtxt:
            readme.write_text(rtxt.replace(marker, block + "\n", 1))

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "SurveyLayout-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
