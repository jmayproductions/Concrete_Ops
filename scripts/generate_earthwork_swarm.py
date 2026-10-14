#!/usr/bin/env python3
"""Generate earthwork / site-civil field swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("earthwork-lead", "EarthworkLead", "Owns earthwork sequence and final GO/HOLD/ABORT.",
     """You own **earthwork / site civil** sequencing and assemble GO/HOLD/ABORT.

## Sequence pattern
1. Survey control + dig ticket / utility locate clear
2. Erosion control installed before mass excavate
3. Excavation to lines/grades; spoil setbacks; shoring when required
4. Subgrade proof-roll / geotech accept before fill or paving
5. Fill in controlled lifts with density tests
6. Trench backfill / bedding for utilities
7. Drainage/swales to plan; paving prep final grade
8. Weather holds for freeze, saturation, or unprotected slopes

Do not invent elevations, densities, or dig-ticket status."""),
    ("survey-control", "SurveyControl", "Owns benchmarks, stakes, and as-built grades.",
     """You own site survey control.

## Checks
- Benchmarks / control points verified
- Cut/fill stakes current to approved grading plan
- As-built grade checks within project tolerance

HOLD missing or disturbed control before excavate/pave."""),
    ("utilities-locate", "UtilitiesLocate", "Owns dig tickets, locates, and soft-dig protocols.",
     """You own utility conflict clearance.

## Checks
- Active dig ticket / 811 ticket valid for work area
- Locates marked; private utilities swept when required
- Soft dig / hand excavate within tolerance of marks
- Unknown lines or conflict => HOLD stop dig

ABORT dig without valid locate or after strike."""),
    ("excavation", "Excavation", "Owns cut to line/grade, spoil, and trench geometry.",
     """You own excavation geometry and spoil control.

## Checks
- Cut to plan lines/grades (no over-excavate without eng direction)
- Spoil set back from crest; haul routes clear
- Trench width/depth and slope or shoring per plan/OSHA class
- Undermining structures/utilities => HOLD

HOLD overcut, spoil encroachment, or unprotected deep trench."""),
    ("subgrade", "Subgrade", "Owns proof-roll, soft spots, and subgrade acceptance.",
     """You own subgrade acceptance.

## Checks
- Proof-roll completed; soft spots mapped
- Undercut/replace of pumping areas complete when required
- Moisture conditioning within project window
- Geotech / SI accept before fill or pavement section

HOLD pumping subgrade or skipped proof-roll."""),
    ("compaction", "Compaction", "Owns lift thickness, moisture, and density tests.",
     """You own controlled fill compaction.

## Checks
- Lift thickness ≤ project max (often 8–12\" loose)
- Moisture near optimum; density ≥ specified % (e.g. 95% Mod)
- Nuclear/sand-cone tests logged per lift/area
- Failures reworked before next lift

HOLD thick lifts or failed density without rework."""),
    ("trench-backfill", "TrenchBackfill", "Owns bedding, shading, and trench compaction.",
     """You own utility trench backfill.

## Checks
- Bedding material and depth per pipe/spec
- Haunching / shading before structural backfill
- Compaction in lifts; no large rocks on pipe
- Trace tape / warning ribbon when required

HOLD missing bedding or uncompacted trench before cover."""),
    ("drainage-swales", "DrainageSwales", "Owns temporary/permanent drainage and swale grades.",
     """You own site drainage during earthwork.

## Checks
- Temporary drainage keeps work area dewatered
- Permanent swales/ditches at design invert/grade
- No ponding against foundations or pavement section
- Culvert/inlet protection in place

HOLD reversed grades or undrained excavations."""),
    ("erosion-control", "ErosionControl", "Owns SWPPP BMPs before and during disturbance.",
     """You own erosion and sediment control.

## Checks
- Perimeter BMPs (silt fence/wattles) installed before mass disturb
- Inlet protection; stabilized construction entrance
- Disturbed slopes mulched/blanketed per SWPPP timing
- Tracking onto public roads controlled

HOLD missing BMPs before clearing/grading."""),
    ("paving-prep", "PavingPrep", "Owns final grade, subbase, and paving release.",
     """You own paving / hardscape prep.

## Checks
- Final grade within tolerance of paving section
- Aggregate base thickness/compaction verified
- Forms/stringlines or stringless control set
- Soft spots corrected; moisture OK for pave day

HOLD base deficient or grade out of tolerance."""),
    ("weather-protect", "WeatherProtect", "Owns freeze, saturation, and storm holds.",
     """You own weather holds for earthwork.

## Holds
- Frozen subgrade/fill without approved procedures
- Saturated / pumping soils placed as structural fill
- Active storm with unprotected open excavations/slopes
- Wind/dust beyond site controls when required

HOLD freeze or saturation risks before fill/pave."""),
    ("geotech", "Geotech", "Owns geotech recommendations and SI hold points.",
     """You own geotechnical acceptance points.

## Checks
- Bearing / subgrade recommendations followed
- Special inspection density tests when specified
- Unsuitable material disposition documented
- Engineer's directive for over-excavate/replace

HOLD missing geotech accept at ITP hold points."""),
    ("materials-fill", "MaterialsFill", "Owns import fill, borrow, and aggregate approvals.",
     """You own fill materials readiness.

## Checks
- Import/borrow approved (gradation, PI, organics)
- Base aggregate certs / sieve when required
- Reject organics, frozen, or oversized for structural fill

HOLD unapproved or contaminated fill on pad."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work authority for trench, utilities, and slopes.",
     """You have stop-work authority. FAIL => swarm **ABORT**.

## Fail conditions
- Dig without valid utility locate / after utility strike
- Unprotected trench/excavation beyond safe slope or shoring
- Spoil or equipment surcharge at crest creating collapse risk
- Unstable slope / cave-in indicators ignored
- Missing competent person for excavations when required"""),
    ("crew-ops", "CrewOps", "Owns roles, briefing, and fatigue for earthwork crews.",
     """You own crew readiness.

## Roles
earthwork_lead, excavator_op, grader_op, roller_op, laborer, qc_tech, safety_watch

HOLD missing roles, incomplete briefing, or fatigue risk."""),
    ("qa-inspector", "QaInspector", "Owns ITP hold points and density/proof-roll evidence.",
     """You own earthwork QA evidence.

## Checks
- Pre-disturb / pre-fill hold points signed
- Density / proof-roll records attached for the phase
- Nonconformances dispositioned before cover/pave

HOLD missing ITP evidence."""),
]

WORKFLOWS = [
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
]

ROLES = (
    "earthwork_lead",
    "excavator_op",
    "grader_op",
    "roller_op",
    "laborer",
    "qc_tech",
    "safety_watch",
)

ORDERS = {
    "pre-earthwork-gate": ["materials-fill", "survey-control", "utilities-locate", "erosion-control", "crew-ops", "weather-protect", "safety-failsafe", "qa-inspector"],
    "utilities-locate-gate": ["utilities-locate", "survey-control", "safety-failsafe", "qa-inspector"],
    "excavation-runbook": ["utilities-locate", "excavation", "survey-control", "weather-protect", "safety-failsafe", "qa-inspector"],
    "subgrade-accept-gate": ["subgrade", "geotech", "weather-protect", "qa-inspector"],
    "compaction-lift-runbook": ["materials-fill", "compaction", "geotech", "weather-protect", "qa-inspector", "safety-failsafe"],
    "trench-backfill-gate": ["utilities-locate", "trench-backfill", "compaction", "safety-failsafe", "qa-inspector"],
    "drainage-swale-qa": ["drainage-swales", "survey-control", "erosion-control", "qa-inspector"],
    "erosion-control-gate": ["erosion-control", "drainage-swales", "weather-protect", "qa-inspector"],
    "paving-prep-gate": ["subgrade", "compaction", "paving-prep", "survey-control", "weather-protect", "qa-inspector", "safety-failsafe"],
    "weather-protect-gate": ["weather-protect", "erosion-control", "safety-failsafe"],
    "earthwork-closeout": ["qa-inspector", "survey-control", "drainage-swales", "erosion-control", "paving-prep", "geotech", "crew-ops"],
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
    Decision: GO | HOLD | ABORT. Prefer EarthworkContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: EarthworkContextJson
    description: JSON context for earthwork excavation fill weather utilities
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    EarthworkContextJson:
      displayName: Earthwork Context JSON
      description: JSON context for earthwork / site civil
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
    agents_root = ROOT / "agents" / "earthwork"
    studio = ROOT / "copilot-studio" / "earthwork-crew"
    mod = ROOT / "modules" / "earthwork_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for Earthwork / Site Civil Swarm

From project `construction.md` extractions and typical civil ITP practice:

- QA/QC Field Procedures – Earthwork / Site Grading (cut/fill, proof-roll, compaction)
- Utility trench excavation & backfill hold points
- SWPPP / erosion & sediment control before disturbance
- Subgrade acceptance and paving prep gates
""")
    write(agents_root / "README.md", """# Earthwork / Site Civil Swarm (reference twin)

> See [`../../copilot-studio/earthwork-crew/`](../../copilot-studio/earthwork-crew/) → `START_HERE.md`.

```bash
python -m modules.earthwork_swarm.cli list
python -m modules.earthwork_swarm.cli run pre-earthwork-gate -c agents/earthwork/fixtures/pre_earthwork_go.yaml
python -m modules.earthwork_swarm.api --port 8088
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# Earthwork Swarm — Coordinator

Return one GO / HOLD / ABORT for site civil / earthwork.

## Hard rules
1. No dig without valid utility locate.
2. No structural fill on pumping/frozen subgrade.
3. Compaction lifts must meet density before next lift / pave.
4. Erosion BMPs before mass disturbance.
5. SafetyFailsafe FAIL → ABORT (trench, utilities, slopes).
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
  componentName: EarthworkSwarm
kind: GptComponentMetadata
displayName: Earthwork Swarm
instructions: |
  You are the Earthwork / Site Civil Swarm coordinator for grading, trench, and paving prep.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect EarthworkContextJson; missing critical fields => HOLD (do not invent readings).
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
  - title: Pre-earthwork gate
    text: Run pre-earthwork-gate for Pad A and return GO/HOLD/ABORT.
  - title: Utilities locate
    text: Run utilities-locate-gate before we dig the sewer trench.
  - title: Compaction lift
    text: Run compaction-lift-runbook — density tests on Lift 3?
  - title: Subgrade accept
    text: Run subgrade-accept-gate after proof-roll.
  - title: Paving prep
    text: Run paving-prep-gate for parking lot section B.
  - title: Erosion control
    text: Run erosion-control-gate before mass clearing.

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: Earthwork Swarm
schemaName: earthwork_swarm
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
          - Earthwork Swarm ready. Ask for pre-earthwork-gate, utilities-locate-gate, compaction-lift-runbook, subgrade-accept-gate, paving-prep-gate, or another named workflow. I return GO / HOLD / ABORT.
          - Earthwork online — share pad/trench context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.earthwork_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for earthwork / site civil QA gates.\n")
    write(studio / "START_HERE.md", """# START HERE — Earthwork Swarm drop-in

Ready Copilot Studio workspace for earthwork / site civil field gates.

## 3 steps
1. Open this `earthwork-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Earthwork Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-earthwork-gate…”*.

## Workflows
`pre-earthwork-gate`, `utilities-locate-gate`, `excavation-runbook`, `subgrade-accept-gate`, `compaction-lift-runbook`, `trench-backfill-gate`, `drainage-swale-qa`, `erosion-control-gate`, `paving-prep-gate`, `weather-protect-gate`, `earthwork-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.earthwork_swarm.api --port 8088
python -m modules.earthwork_swarm.cli run pre-earthwork-gate -c agents/earthwork/fixtures/pre_earthwork_go.yaml
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

    agents_src = r'''"""Deterministic specialist gates for earthwork / site civil."""

from __future__ import annotations

from typing import Any

from modules.earthwork_swarm.schemas import GateResult

ERECT_ROLES = __ROLES__
DEFAULT_MAX_LIFT_IN = 12.0


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class MaterialsFillAgent:
    name = "materials-fill"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("materials") or {}
        if m.get("required") is False:
            return GateResult(self.name, "PASS", "No import fill this gate", {"materials": m})
        miss = _missing(m, ("import_approved", "organics_ok", "aggregate_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Fill materials incomplete: " + ", ".join(miss), {"materials": m})
        if m.get("contaminated") or m.get("frozen_load"):
            return GateResult(self.name, "HOLD", "Contaminated or frozen fill rejected", {"materials": m})
        return GateResult(self.name, "PASS", "Fill/aggregate materials clear", {"materials": m})


class SurveyControlAgent:
    name = "survey-control"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("survey") or {}
        miss = _missing(s, ("benchmarks_ok", "stakes_current"))
        if miss:
            return GateResult(self.name, "HOLD", "Survey control incomplete: " + ", ".join(miss), {"survey": s})
        if s.get("grade_out_of_tolerance"):
            return GateResult(self.name, "HOLD", "Grade out of tolerance — re-stake/rework", {"survey": s})
        return GateResult(self.name, "PASS", "Survey/control clear", {"survey": s})


class UtilitiesLocateAgent:
    name = "utilities-locate"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        u = ctx.get("utilities") or {}
        if u.get("dig_without_locate") or u.get("utility_strike"):
            return GateResult(self.name, "FAIL", "STOP-WORK: dig without locate or utility strike", {"utilities": u})
        miss = _missing(u, ("ticket_valid", "marks_visible"))
        if miss:
            return GateResult(self.name, "HOLD", "Utility locate incomplete: " + ", ".join(miss), {"utilities": u})
        if u.get("conflict_unresolved"):
            return GateResult(self.name, "HOLD", "Utility conflict unresolved — soft dig / redesign", {"utilities": u})
        return GateResult(self.name, "PASS", "Utility locate clear", {"utilities": u})


class ExcavationAgent:
    name = "excavation"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("excavation") or {}
        if e.get("overcut_unapproved"):
            return GateResult(self.name, "HOLD", "Over-excavation without engineer direction", {"excavation": e})
        if e.get("spoil_at_crest"):
            return GateResult(self.name, "HOLD", "Spoil surcharge at crest — pull back", {"excavation": e})
        if e.get("unprotected_deep"):
            return GateResult(self.name, "FAIL", "Unprotected deep excavation / trench", {"excavation": e})
        if e.get("to_plan") is False:
            return GateResult(self.name, "HOLD", "Excavation not to plan lines/grades", {"excavation": e})
        return GateResult(self.name, "PASS", "Excavation geometry clear", {"excavation": e})


class SubgradeAgent:
    name = "subgrade"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("subgrade") or {}
        if not s.get("proof_roll_done"):
            return GateResult(self.name, "HOLD", "Proof-roll not completed", {"subgrade": s})
        if s.get("pumping") or s.get("soft_spots_open"):
            return GateResult(self.name, "HOLD", "Pumping/soft spots not undercut/replaced", {"subgrade": s})
        if s.get("accepted") is False:
            return GateResult(self.name, "HOLD", "Subgrade not accepted", {"subgrade": s})
        return GateResult(self.name, "PASS", "Subgrade acceptance clear", {"subgrade": s})


class CompactionAgent:
    name = "compaction"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("compaction") or {}
        if c.get("required") is False:
            return GateResult(self.name, "PASS", "No compaction this gate", {"compaction": c})
        lift = _num(c.get("lift_in"))
        max_lift = _num(c.get("max_lift_in"), DEFAULT_MAX_LIFT_IN) or DEFAULT_MAX_LIFT_IN
        if lift is not None and lift > max_lift:
            return GateResult(self.name, "HOLD", f"Lift {lift}in > {max_lift}in max", {"compaction": c})
        if c.get("density_ok") is False:
            return GateResult(self.name, "HOLD", "Density test failed — rework lift", {"compaction": c})
        if c.get("moisture_ok") is False:
            return GateResult(self.name, "HOLD", "Moisture out of window", {"compaction": c})
        if not c.get("tests_logged"):
            return GateResult(self.name, "HOLD", "Density tests not logged for lift/area", {"compaction": c})
        return GateResult(self.name, "PASS", "Compaction lifts clear", {"compaction": c})


class TrenchBackfillAgent:
    name = "trench-backfill"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("trench") or {}
        if not t and not ctx.get("require_trench"):
            return GateResult(self.name, "SKIP", "No trench scope", {})
        miss = _missing(t, ("bedding_ok", "haunching_ok", "compacted"))
        if miss:
            return GateResult(self.name, "HOLD", "Trench backfill incomplete: " + ", ".join(miss), {"trench": t})
        if t.get("rocks_on_pipe"):
            return GateResult(self.name, "HOLD", "Oversized rock on pipe — rework shading", {"trench": t})
        return GateResult(self.name, "PASS", "Trench backfill clear", {"trench": t})


class DrainageSwalesAgent:
    name = "drainage-swales"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("drainage") or {}
        if d.get("ponding"):
            return GateResult(self.name, "HOLD", "Ponding against work / foundations", {"drainage": d})
        if d.get("grade_reversed"):
            return GateResult(self.name, "HOLD", "Swale/ditch grade reversed", {"drainage": d})
        if not d.get("temp_drainage_ok") and not d.get("permanent_ok"):
            return GateResult(self.name, "HOLD", "No temporary or permanent drainage confirmed", {"drainage": d})
        return GateResult(self.name, "PASS", "Drainage/swales clear", {"drainage": d})


class ErosionControlAgent:
    name = "erosion-control"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("erosion") or {}
        if not e.get("perimeter_bmps"):
            return GateResult(self.name, "HOLD", "Perimeter BMPs missing before disturb", {"erosion": e})
        if e.get("inlet_protection") is False:
            return GateResult(self.name, "HOLD", "Inlet protection missing/deficient", {"erosion": e})
        if e.get("entrance_stabilized") is False:
            return GateResult(self.name, "HOLD", "Construction entrance not stabilized", {"erosion": e})
        return GateResult(self.name, "PASS", "Erosion control clear", {"erosion": e})


class PavingPrepAgent:
    name = "paving-prep"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("paving") or {}
        if not p and not ctx.get("require_paving"):
            return GateResult(self.name, "SKIP", "No paving prep scope", {})
        miss = _missing(p, ("final_grade_ok", "base_thickness_ok", "base_compacted"))
        if miss:
            return GateResult(self.name, "HOLD", "Paving prep incomplete: " + ", ".join(miss), {"paving": p})
        if p.get("soft_spots"):
            return GateResult(self.name, "HOLD", "Soft spots remain in pave section", {"paving": p})
        return GateResult(self.name, "PASS", "Paving prep clear", {"paving": p})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        holds = []
        if w.get("frozen_subgrade") and not w.get("freeze_procedures"):
            holds.append("frozen subgrade/fill without procedures")
        if w.get("saturated") and not w.get("dry_workable"):
            holds.append("saturated/pumping soils for structural fill")
        if w.get("active_storm") and not w.get("slopes_protected"):
            holds.append("storm with unprotected open excavations/slopes")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/protection CLEAR", {"weather": w})


class GeotechAgent:
    name = "geotech"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("geotech") or {}
        if g.get("required") is False:
            return GateResult(self.name, "PASS", "Geotech hold not required this gate", {"geotech": g})
        if not g.get("recommendations_followed"):
            return GateResult(self.name, "HOLD", "Geotech recommendations not followed", {"geotech": g})
        if g.get("si_density_required") and not g.get("si_density_complete"):
            return GateResult(self.name, "HOLD", "Special inspection density tests incomplete", {"geotech": g})
        if not g.get("accepted"):
            return GateResult(self.name, "HOLD", "Geotech acceptance missing", {"geotech": g})
        return GateResult(self.name, "PASS", "Geotech hold points clear", {"geotech": g})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        u = ctx.get("utilities") or {}
        e = ctx.get("excavation") or {}
        if u.get("dig_without_locate") or u.get("utility_strike"):
            violations.append("utility locate strike / dig without ticket")
        if e.get("unprotected_deep"):
            violations.append("unprotected deep excavation")
        if e.get("spoil_at_crest") and e.get("collapse_risk"):
            violations.append("spoil surcharge collapse risk")
        if ctx.get("slope", {}).get("unstable"):
            violations.append("unstable slope / cave-in indicators")
        if s.get("no_competent_person") and (e.get("depth_ft") or 0) >= 5:
            violations.append("no excavation competent person")
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
            return GateResult(self.name, "PASS", "Pre-earthwork QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class EarthworkLeadAgent:
    name = "earthwork-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked earthwork"
        elif any(g.agent == "utilities-locate" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Utility locate fail-safe blocked dig"
        elif any(g.agent == "excavation" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Excavation safety blocked dig"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named earthwork workflow runners."""

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
''')

    write(mod / "swarm.py", '''"""Earthwork swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.earthwork_swarm.schemas import SwarmResult
from modules.earthwork_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class EarthworkSwarm:
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
        log_event(f"[earthwork-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[earthwork-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["EarthworkSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.earthwork_swarm.swarm import EarthworkSwarm, SwarmResult
from modules.earthwork_swarm.workflows import WORKFLOW_IDS

__all__ = ["EarthworkSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for earthwork swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.earthwork_swarm.swarm import EarthworkSwarm

app = typer.Typer(add_completion=False, help="Earthwork / site civil field swarm")


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
    for w in EarthworkSwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = EarthworkSwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "earthwork" / "fixtures" / "pre_earthwork_go.yaml"
    result = EarthworkSwarm().run("pre-earthwork-gate", yaml.safe_load(fixture.read_text()))
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

from modules.earthwork_swarm.swarm import EarthworkSwarm
from modules.earthwork_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = EarthworkSwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[earthwork-swarm-api] {self.address_string()} {fmt % args}")

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
        if isinstance(payload.get("EarthworkContextJson"), str):
            try:
                context = {**context, **json.loads(payload["EarthworkContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "EarthworkContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8088)
    args = p.parse_args()
    print(f"Earthwork swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-PAD-A
area: Pad A mass grade
materials:
  import_approved: true
  organics_ok: true
  aggregate_ok: true
  contaminated: false
  frozen_load: false
survey:
  benchmarks_ok: true
  stakes_current: true
  grade_out_of_tolerance: false
utilities:
  ticket_valid: true
  marks_visible: true
  conflict_unresolved: false
  dig_without_locate: false
  utility_strike: false
excavation:
  to_plan: true
  overcut_unapproved: false
  spoil_at_crest: false
  unprotected_deep: false
  depth_ft: 4
subgrade:
  proof_roll_done: true
  pumping: false
  soft_spots_open: false
  accepted: true
compaction:
  lift_in: 8
  max_lift_in: 12
  density_ok: true
  moisture_ok: true
  tests_logged: true
trench:
  bedding_ok: true
  haunching_ok: true
  compacted: true
  rocks_on_pipe: false
drainage:
  temp_drainage_ok: true
  permanent_ok: true
  ponding: false
  grade_reversed: false
erosion:
  perimeter_bmps: true
  inlet_protection: true
  entrance_stabilized: true
paving:
  final_grade_ok: true
  base_thickness_ok: true
  base_compacted: true
  soft_spots: false
weather:
  frozen_subgrade: false
  saturated: false
  dry_workable: true
  active_storm: false
  slopes_protected: true
  freeze_procedures: true
geotech:
  recommendations_followed: true
  si_density_required: true
  si_density_complete: true
  accepted: true
crew:
  roles:
    - earthwork_lead
    - excavator_op
    - grader_op
    - roller_op
    - laborer
    - qc_tech
    - safety_watch
  headcount: 10
  briefing_complete: true
  fatigued_workers: []
qa:
  pre_hold_points_clear: true
  install_hold_points_clear: true
safety:
  violations: []
  no_competent_person: false
"""
    write(agents_root / "fixtures" / "pre_earthwork_go.yaml", go)
    write(studio / "samples" / "pre_earthwork_go.yaml", go)
    write(agents_root / "fixtures" / "density_fail_hold.yaml", """zone_id: DEMO-PAD-A
materials:
  import_approved: true
  organics_ok: true
  aggregate_ok: true
compaction:
  lift_in: 8
  max_lift_in: 12
  density_ok: false
  moisture_ok: true
  tests_logged: true
geotech:
  recommendations_followed: true
  si_density_required: true
  si_density_complete: true
  accepted: true
weather:
  frozen_subgrade: false
  saturated: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "no_locate_abort.yaml", """zone_id: DEMO-SEWER-TRENCH
utilities:
  ticket_valid: false
  marks_visible: false
  dig_without_locate: true
survey:
  benchmarks_ok: true
  stakes_current: true
excavation:
  to_plan: true
  depth_ft: 6
weather:
  frozen_subgrade: false
  saturated: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "pumping_subgrade_hold.yaml", """zone_id: DEMO-PAD-A
subgrade:
  proof_roll_done: true
  pumping: true
  soft_spots_open: true
  accepted: false
geotech:
  recommendations_followed: false
  accepted: false
weather:
  frozen_subgrade: false
  saturated: true
  dry_workable: false
qa:
  install_hold_points_clear: true
""")
    write(agents_root / "fixtures" / "unprotected_trench_abort.yaml", """zone_id: DEMO-SEWER-TRENCH
utilities:
  ticket_valid: true
  marks_visible: true
excavation:
  to_plan: true
  unprotected_deep: true
  depth_ft: 8
  spoil_at_crest: true
  collapse_risk: true
survey:
  benchmarks_ok: true
  stakes_current: true
weather:
  frozen_subgrade: false
  saturated: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
  no_competent_person: true
""")
    write(agents_root / "fixtures" / "bmps_missing_hold.yaml", """zone_id: DEMO-PAD-A
materials:
  import_approved: true
  organics_ok: true
  aggregate_ok: true
survey:
  benchmarks_ok: true
  stakes_current: true
utilities:
  ticket_valid: true
  marks_visible: true
erosion:
  perimeter_bmps: false
  inlet_protection: false
  entrance_stabilized: false
weather:
  frozen_subgrade: false
  saturated: false
crew:
  roles: [earthwork_lead, excavator_op, grader_op, roller_op, laborer, qc_tech, safety_watch]
  briefing_complete: true
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")

    write(ROOT / "tests" / "test_earthwork_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.earthwork_swarm.swarm import EarthworkSwarm
from modules.earthwork_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "earthwork" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(EarthworkSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_earthwork_go():
    assert EarthworkSwarm().run("pre-earthwork-gate", _load("pre_earthwork_go.yaml")).decision == "GO"


def test_density_fail_hold():
    assert EarthworkSwarm().run("compaction-lift-runbook", _load("density_fail_hold.yaml")).decision == "HOLD"


def test_no_locate_abort():
    assert EarthworkSwarm().run("utilities-locate-gate", _load("no_locate_abort.yaml")).decision == "ABORT"


def test_pumping_subgrade_hold():
    assert EarthworkSwarm().run("subgrade-accept-gate", _load("pumping_subgrade_hold.yaml")).decision == "HOLD"


def test_unprotected_trench_abort():
    assert EarthworkSwarm().run("excavation-runbook", _load("unprotected_trench_abort.yaml")).decision == "ABORT"


def test_bmps_missing_hold():
    assert EarthworkSwarm().run("pre-earthwork-gate", _load("bmps_missing_hold.yaml")).decision == "HOLD"


def test_compaction_go():
    assert EarthworkSwarm().run("compaction-lift-runbook", _load("pre_earthwork_go.yaml")).decision == "GO"


def test_paving_prep_go():
    assert EarthworkSwarm().run("paving-prep-gate", _load("pre_earthwork_go.yaml")).decision == "GO"


def test_hold_abort():
    assert EarthworkSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "utility strike"}).decision == "ABORT"
''')

    # Keep zip binary attrs (same as sibling swarms)
    gitattributes = ROOT / ".gitattributes"
    text = gitattributes.read_text() if gitattributes.exists() else ""
    if "*.zip binary" not in text:
        if not text.endswith("\n"):
            text += "\n"
        text += "\n*.zip binary\npackages/**/*.zip binary\n"
        gitattributes.write_text(text)

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "EarthworkSiteCivil-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
