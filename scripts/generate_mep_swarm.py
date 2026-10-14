#!/usr/bin/env python3
"""Generate MEP rough-in + firestop field swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("mep-lead", "MepLead", "Owns MEP rough-in sequence and final GO/HOLD/ABORT.",
     """You own **MEP rough-in + firestop** sequencing and assemble GO/HOLD/ABORT.

## Sequence pattern
1. BIM clash clear + sleeve/penetration map published
2. Layout / hangers / supports before cover
3. HVAC duct / electrical / plumbing rough per trade gates
4. Fire/smoke dampers accessible and tagged
5. Firestop: UL system match, photo before cover — no wall/ceiling close without log
6. Pressure / DALT / insulation resistance tests as required
7. Shaft / in-wall inspection before cover; commissioning prep

Do not invent pressures, ohms, or UL system IDs."""),
    ("clash-coord", "ClashCoord", "Owns BIM clash resolution before in-wall inspection.",
     """You own MEP coordination / clash clearance.

## Checks
- Clash resolution complete for the zone before in-wall / cover
- Sleeve/opening map published and matched to installs
- Unresolved hard clashes => HOLD
- RFI filed for drawing conflicts with sheet/detail/photo

HOLD unresolved clashes before cover inspection."""),
    ("sleeve-penetration", "SleevePenetration", "Owns cores, sleeves, and penetration coordination.",
     """You own sleeves / cores / penetrations.

## Checks
- Sleeve placement vs opening map
- Offset within project tolerance (halt if grossly mislocated)
- Penetrations sized for firestop system
- Structural penetrations only where sleeved/specified

HOLD missing sleeves on rated assemblies."""),
    ("hvac-rough", "HvacRough", "Owns ductwork, hangers, insulation, VAV, dampers.",
     """You own HVAC rough-in QA.

## Checks
- Duct seams sealed (SMACNA level per project)
- Hanger spacing per size/spec
- Insulation R-value compliance
- VAV/equipment placed; controls path available
- Fire/smoke dampers installed, accessible, tagged

HOLD incomplete dampers or missing hangers on main runs."""),
    ("electrical-rough", "ElectricalRough", "Owns conduit, wire fill, panels, grounding.",
     """You own electrical rough-in QA.

## Checks
- Conduit anchored per spacing; bend/fill limits
- Wire pull without damage; fill ≤ project max (often 40%)
- Panels labeled, bonded, plumb
- Grounding / insulation resistance tests when required

HOLD failed grounding/IR tests or overfill."""),
    ("plumbing-rough", "PlumbingRough", "Owns DWV slope, water supply, hydro tests.",
     """You own plumbing rough QA.

## Checks
- DWV slope per project (typical 1/4\"/ft)
- Expansion joints as specified
- Hydrostatic / pressure tests held per project (no drop beyond limit)
- No leaks; gauge stable

HOLD failed pressure tests or reverse/insufficient slope."""),
    ("firestop", "Firestop", "Owns UL firestop assemblies, labels, and pre-cover photos.",
     """You own firestopping field protocol.

## Rules
- Identify wall/floor rating (1-hr, 2-hr, smoke, etc.)
- Match UL assembly ID (e.g. W-L-#### / C-AJ-####) to penetration type 100%
- Approved sealant, backing, wrap used
- Photo evidence + label before covering wall/ceiling
- Firestop inspected before wallboard / close-out

FAIL wrong UL system or cover without inspection.
HOLD incomplete firestop log."""),
    ("damper-life-safety", "DamperLifeSafety", "Owns fire/smoke damper install, access, and actuation.",
     """You own fire/smoke dampers and related life-safety devices in MEP path.

## Checks
- Damper type matches rating / schedule
- Access door provided and clear
- Actuation / close test when required (auto shut within project time)
- Tagged and on inspection log

HOLD inaccessible or untested required dampers."""),
    ("shaft-access", "ShaftAccess", "Owns vertical shaft routing, clearances, and access panels.",
     """You own service shaft QA.

## Checks
- Trade sequence / access plan for shaft
- Stack clearances per spec
- Access hatches present where required
- No blocked maintenance paths

HOLD missing access hatch or stack clearance conflict."""),
    ("pressure-test", "PressureTest", "Owns hydro, DALT, and pneumatic test evidence.",
     """You own MEP pressure / leakage testing.

## Checks
- Method and acceptance criteria recorded (hydro, air, DALT)
- Duration / pressure held; gauge evidence
- Failures mapped with owner/retest

HOLD required test not performed.
FAIL active leak beyond acceptance (treat as HOLD at parent unless safety)."""),
    ("insulation-hangers", "InsulationHangers", "Owns supports, hangers, and MEP insulation.",
     """You own hangers and insulation.

## Checks
- Hanger spacing / trapeze adequacy
- Vibration isolation where specified
- Insulation complete on required ducts/pipes before cover
- No crushed insulation at supports

HOLD missing required insulation on covered runs."""),
    ("labeling-asbuilt", "LabelingAsbuilt", "Owns valve/panel labels, QR tags, and redlines.",
     """You own labeling and as-built capture.

## Checks
- Valves, panels, dampers labeled
- Penetration / firestop tags match log
- Redlines updated for relocated services
- Weekly upload cadence when project requires

HOLD unlabeled critical devices before cover/close."""),
    ("weather-gate", "WeatherGate", "Owns weather holds for exterior MEP and open shafts.",
     """You own weather holds affecting MEP rough-in.

## Holds
- Exterior work in lightning / high wind
- Freeze risk for water testing without protection
- Open shaft weather exposure damaging materials

Missing weather when exterior scope => HOLD."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work authority for MEP / firestop / energized work.",
     """Stop-work for MEP rough-in and firestop.

## Immediate ABORT
- Energized work without LOTO
- Confined space / shaft entry without controls
- Covering rated penetration without firestop (willful)
- Hot-work in shaft without permit

SafetyFailsafe FAIL => parent Decision ABORT."""),
    ("crew-ops", "CrewOps", "Owns MEP crew roles, fatigue, and briefing.",
     """You own MEP crew readiness.

## Typical roles
mep_lead, hvac_tech, electrician, plumber, firestop_tech, qc_tech, safety_watch

HOLD missing roles or incomplete briefing."""),
    ("qa-inspector", "QaInspector", "Owns MEP/firestop hold points, photos, and NCRs.",
     """You own MEP/firestop QC evidence.

## Evidence
- Pre-cover hold points clear
- Firestop log signed; UL IDs photographed
- Pressure/DALT/IR test reports as required
- NCRs with reinspect

Missing phase evidence => HOLD."""),
]

WORKFLOWS = [
    "pre-mep-gate",
    "clash-sleeve-gate",
    "hvac-rough-runbook",
    "electrical-rough-runbook",
    "plumbing-rough-runbook",
    "firestop-precover-gate",
    "damper-life-safety-gate",
    "shaft-inspection-gate",
    "pressure-test-gate",
    "inwall-cover-release",
    "mep-closeout",
    "hold-abort",
]

ROLES = (
    "mep_lead",
    "hvac_tech",
    "electrician",
    "plumber",
    "firestop_tech",
    "qc_tech",
    "safety_watch",
)

ORDERS = {
    "pre-mep-gate": ["clash-coord", "sleeve-penetration", "crew-ops", "weather-gate", "safety-failsafe", "qa-inspector"],
    "clash-sleeve-gate": ["clash-coord", "sleeve-penetration", "qa-inspector", "safety-failsafe"],
    "hvac-rough-runbook": ["hvac-rough", "insulation-hangers", "damper-life-safety", "qa-inspector", "safety-failsafe"],
    "electrical-rough-runbook": ["electrical-rough", "labeling-asbuilt", "qa-inspector", "safety-failsafe"],
    "plumbing-rough-runbook": ["plumbing-rough", "pressure-test", "insulation-hangers", "qa-inspector", "safety-failsafe"],
    "firestop-precover-gate": ["firestop", "sleeve-penetration", "qa-inspector", "safety-failsafe"],
    "damper-life-safety-gate": ["damper-life-safety", "hvac-rough", "qa-inspector", "safety-failsafe"],
    "shaft-inspection-gate": ["shaft-access", "clash-coord", "firestop", "qa-inspector", "safety-failsafe"],
    "pressure-test-gate": ["pressure-test", "plumbing-rough", "hvac-rough", "qa-inspector"],
    "inwall-cover-release": ["clash-coord", "firestop", "hvac-rough", "electrical-rough", "plumbing-rough", "qa-inspector", "safety-failsafe"],
    "mep-closeout": ["qa-inspector", "firestop", "pressure-test", "labeling-asbuilt", "damper-life-safety", "crew-ops"],
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
    Decision: GO | HOLD | ABORT. Prefer MepContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: MepContextJson
    description: JSON context for MEP zone sleeves firestop tests crew
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    MepContextJson:
      displayName: MEP Context JSON
      description: JSON context for MEP rough-in / firestop
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
    agents_root = ROOT / "agents" / "mep"
    studio = ROOT / "copilot-studio" / "mep-crew"
    mod = ROOT / "modules" / "mep_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for MEP Rough-In + Firestop Swarm

From project `construction.md` extractions:

- QA/QC Field Procedures – MEP Rough-In and Systems Integration (HVAC / Electrical / Plumbing)
- Elevation-Firestop-Ceiling QA + RFI/As-Built Protocol (UL firestop before cover)
- MEP Penetration + Sleeve Coordination, Service Shaft QA, Service Clash Detection
- Fire Protection System QA (dampers / NFPA class tests)
""")
    write(agents_root / "README.md", """# MEP Rough-In + Firestop Swarm (reference twin)

> See [`../../copilot-studio/mep-crew/`](../../copilot-studio/mep-crew/) → `START_HERE.md`.

```bash
python -m modules.mep_swarm.cli list
python -m modules.mep_swarm.cli run pre-mep-gate -c agents/mep/fixtures/pre_mep_go.yaml
python -m modules.mep_swarm.api --port 8084
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# MEP Rough-In + Firestop Swarm — Coordinator

Return one GO / HOLD / ABORT for MEP rough-in and firestop.

## Hard rules
1. No cover with unresolved clashes or incomplete firestop log.
2. UL assembly ID must match submittal for each penetration type.
3. Photo + label firestop before wallboard / ceiling close.
4. Required pressure/DALT/IR tests before closeout.
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
  componentName: MepFirestopSwarm
kind: GptComponentMetadata
displayName: MEP Firestop Swarm
instructions: |
  You are the MEP Rough-In + Firestop Swarm coordinator for HVAC, electrical,
  plumbing rough-in, sleeves/penetrations, UL firestop, dampers, and shafts.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect MepContextJson; missing critical fields => HOLD (do not invent readings).
  3. Invoke child agents IN DOCUMENTED ORDER for that workflow.
  4. Wait for Decision/Summary/GatesJson/ActionsJson from each child.
  5. One parent reply only. Children must not reply to the field user.
  6. SafetyFailsafe FAIL => final Decision ABORT.
  7. Never release wall/ceiling cover without signed firestop log + photos.

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
  - title: Pre-MEP gate
    text: Run pre-mep-gate for Level 2 Zone C and return GO/HOLD/ABORT.
  - title: Clash/sleeves
    text: Run clash-sleeve-gate before we start in-wall rough.
  - title: Firestop pre-cover
    text: Run firestop-precover-gate — UL logs complete for rated corridor walls?
  - title: Plumbing pressure
    text: Run pressure-test-gate for domestic water Level 2.
  - title: In-wall cover
    text: Run inwall-cover-release for Area B before drywall.
  - title: Shaft inspection
    text: Run shaft-inspection-gate for Stair 2 MEP shaft.

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: MEP Firestop Swarm
schemaName: mep_firestopSwarm
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
          - MEP Firestop Swarm ready. Ask for pre-mep-gate, firestop-precover-gate, inwall-cover-release, pressure-test-gate, or another named workflow. I return GO / HOLD / ABORT.
          - MEP rough-in online — share zone context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.mep_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for MEP rough-in + UL firestop + shafts/dampers.\n")
    write(studio / "START_HERE.md", """# START HERE — MEP Firestop Swarm drop-in

Ready Copilot Studio workspace for MEP rough-in and firestop.

## 3 steps
1. Open this `mep-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **MEP Firestop Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-mep-gate…”*.

## Workflows
`pre-mep-gate`, `clash-sleeve-gate`, `hvac-rough-runbook`, `electrical-rough-runbook`, `plumbing-rough-runbook`, `firestop-precover-gate`, `damper-life-safety-gate`, `shaft-inspection-gate`, `pressure-test-gate`, `inwall-cover-release`, `mep-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.mep_swarm.api --port 8084
python -m modules.mep_swarm.cli run pre-mep-gate -c agents/mep/fixtures/pre_mep_go.yaml
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

    agents_src = r'''"""Deterministic specialist gates for MEP rough-in + firestop."""

from __future__ import annotations

from typing import Any

from modules.mep_swarm.schemas import GateResult

ERECT_ROLES = __ROLES__


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class ClashCoordAgent:
    name = "clash-coord"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("clash") or {}
        if c.get("resolved") is False or c.get("unresolved"):
            return GateResult(self.name, "HOLD", "Unresolved MEP clashes: " + ", ".join(c.get("unresolved") or ["see BIM"]), {"clash": c})
        if not c.get("sleeve_map_published"):
            return GateResult(self.name, "HOLD", "Sleeve/opening map not published", {"clash": c})
        return GateResult(self.name, "PASS", "Clash/coordination clear", {"clash": c})


class SleevePenetrationAgent:
    name = "sleeve-penetration"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("sleeves") or {}
        if not s.get("placed_per_map"):
            return GateResult(self.name, "HOLD", "Sleeves not placed per opening map", {"sleeves": s})
        if s.get("gross_offset"):
            return GateResult(self.name, "HOLD", "Sleeve offset beyond tolerance — halt and re-core/plan", {"sleeves": s})
        if s.get("missing_on_rated"):
            return GateResult(self.name, "HOLD", "Missing sleeves on rated assemblies: " + ", ".join(s["missing_on_rated"]), {"sleeves": s})
        return GateResult(self.name, "PASS", "Sleeves/penetrations clear", {"sleeves": s})


class HvacRoughAgent:
    name = "hvac-rough"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        h = ctx.get("hvac") or {}
        if not h and not ctx.get("require_hvac"):
            return GateResult(self.name, "SKIP", "No HVAC scope", {})
        miss = _missing(h, ("seams_sealed", "hangers_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "HVAC incomplete: " + ", ".join(miss), {"hvac": h})
        if h.get("dampers_incomplete"):
            return GateResult(self.name, "HOLD", "Fire/smoke dampers incomplete/inaccessible", {"hvac": h})
        return GateResult(self.name, "PASS", "HVAC rough clear", {"hvac": h})


class ElectricalRoughAgent:
    name = "electrical-rough"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("electrical") or {}
        if not e and not ctx.get("require_electrical"):
            return GateResult(self.name, "SKIP", "No electrical scope", {})
        miss = _missing(e, ("conduit_ok", "fill_ok", "panels_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Electrical incomplete: " + ", ".join(miss), {"electrical": e})
        if e.get("grounding_fail") or e.get("ir_fail"):
            return GateResult(self.name, "HOLD", "Grounding/IR test failed", {"electrical": e})
        return GateResult(self.name, "PASS", "Electrical rough clear", {"electrical": e})


class PlumbingRoughAgent:
    name = "plumbing-rough"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("plumbing") or {}
        if not p and not ctx.get("require_plumbing"):
            return GateResult(self.name, "SKIP", "No plumbing scope", {})
        if p.get("slope_ok") is False:
            return GateResult(self.name, "HOLD", "DWV slope insufficient/reversed", {"plumbing": p})
        miss = _missing(p, ("layout_ok",))
        if miss:
            return GateResult(self.name, "HOLD", "Plumbing incomplete: " + ", ".join(miss), {"plumbing": p})
        return GateResult(self.name, "PASS", "Plumbing rough clear", {"plumbing": p})


class FirestopAgent:
    name = "firestop"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("firestop") or {}
        if f.get("required") is False:
            return GateResult(self.name, "PASS", "No firestop scope this zone", {"firestop": f})
        if f.get("wrong_ul_system"):
            return GateResult(self.name, "FAIL", "UL system mismatch vs submittal", {"firestop": f})
        if f.get("covered_without_inspection"):
            return GateResult(self.name, "FAIL", "Rated penetration covered without firestop inspection", {"firestop": f})
        miss = _missing(f, ("ul_matched", "photos_before_cover", "log_signed"))
        if miss:
            return GateResult(self.name, "HOLD", "Firestop incomplete: " + ", ".join(miss), {"firestop": f})
        return GateResult(self.name, "PASS", "Firestop pre-cover clear", {"firestop": f})


class DamperLifeSafetyAgent:
    name = "damper-life-safety"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("dampers") or {}
        if not d and not ctx.get("require_dampers"):
            return GateResult(self.name, "SKIP", "No damper scope", {})
        miss = _missing(d, ("installed", "accessible", "tagged"))
        if miss:
            return GateResult(self.name, "HOLD", "Dampers incomplete: " + ", ".join(miss), {"dampers": d})
        if d.get("actuation_required") and not d.get("actuation_passed"):
            return GateResult(self.name, "HOLD", "Damper actuation/close test not passed", {"dampers": d})
        return GateResult(self.name, "PASS", "Damper/life-safety clear", {"dampers": d})


class ShaftAccessAgent:
    name = "shaft-access"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("shaft") or {}
        if not s and not ctx.get("require_shaft"):
            return GateResult(self.name, "SKIP", "No shaft scope", {})
        if s.get("missing_access_hatch"):
            return GateResult(self.name, "HOLD", "Missing required shaft access hatch", {"shaft": s})
        if s.get("clearance_conflict"):
            return GateResult(self.name, "HOLD", "Stack clearance conflict", {"shaft": s})
        if not s.get("trade_sequence_ok"):
            return GateResult(self.name, "HOLD", "Shaft trade sequence/access plan incomplete", {"shaft": s})
        return GateResult(self.name, "PASS", "Shaft access/routing clear", {"shaft": s})


class PressureTestAgent:
    name = "pressure-test"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("pressure_test") or {}
        if t.get("required") is False:
            return GateResult(self.name, "PASS", "Pressure/DALT not required this gate", {"pressure_test": t})
        if not t.get("performed"):
            return GateResult(self.name, "HOLD", "Required pressure/DALT/IR test not performed", {"pressure_test": t})
        if t.get("passed") is False:
            return GateResult(self.name, "FAIL", f"Test failed: {t.get('notes', 'see report')}", {"pressure_test": t})
        return GateResult(self.name, "PASS", "Pressure/leakage tests clear", {"pressure_test": t})


class InsulationHangersAgent:
    name = "insulation-hangers"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        i = ctx.get("insulation") or {}
        if not i:
            return GateResult(self.name, "SKIP", "No insulation/hanger gate", {})
        if i.get("hangers_ok") is False:
            return GateResult(self.name, "HOLD", "Hanger spacing/support deficient", {"insulation": i})
        if i.get("insulation_complete") is False:
            return GateResult(self.name, "HOLD", "Required insulation incomplete before cover", {"insulation": i})
        return GateResult(self.name, "PASS", "Insulation/hangers clear", {"insulation": i})


class LabelingAsbuiltAgent:
    name = "labeling-asbuilt"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("labeling") or {}
        if not l:
            return GateResult(self.name, "SKIP", "No labeling scope", {})
        if l.get("critical_unlabeled"):
            return GateResult(self.name, "HOLD", "Unlabeled devices: " + ", ".join(l["critical_unlabeled"]), {"labeling": l})
        if l.get("redlines_current") is False:
            return GateResult(self.name, "HOLD", "As-built redlines not current", {"labeling": l})
        return GateResult(self.name, "PASS", "Labeling/as-builts clear", {"labeling": l})


class WeatherGateAgent:
    name = "weather-gate"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            if ctx.get("exterior_scope"):
                return GateResult(self.name, "HOLD", "No weather data for exterior MEP", {})
            return GateResult(self.name, "PASS", "Interior scope — weather N/A", {})
        holds = []
        if w.get("lightning"):
            holds.append("lightning")
        wind = _num(w.get("wind_kph"), 0) or 0
        if wind >= (_num(w.get("wind_hold_kph"), 55) or 55):
            holds.append(f"wind {wind}kph")
        if w.get("freeze_risk") and w.get("water_test_exposed"):
            holds.append("freeze risk during water test")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather CLEAR", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("electrical", {}).get("energized_without_loto"):
            violations.append("energized work without LOTO")
        if ctx.get("firestop", {}).get("covered_without_inspection"):
            violations.append("covering rated penetration without firestop inspection")
        if ctx.get("shaft", {}).get("entry_without_controls"):
            violations.append("shaft entry without controls")
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
            return GateResult(self.name, "PASS", "Pre-MEP QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class MepLeadAgent:
    name = "mep-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked MEP work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named MEP rough-in + firestop workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.mep_swarm.agents import (
    ClashCoordAgent,
    CrewOpsAgent,
    DamperLifeSafetyAgent,
    ElectricalRoughAgent,
    FirestopAgent,
    HvacRoughAgent,
    InsulationHangersAgent,
    LabelingAsbuiltAgent,
    MepLeadAgent,
    PlumbingRoughAgent,
    PressureTestAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    ShaftAccessAgent,
    SleevePenetrationAgent,
    WeatherGateAgent,
)
from modules.mep_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-mep-gate",
    "clash-sleeve-gate",
    "hvac-rough-runbook",
    "electrical-rough-runbook",
    "plumbing-rough-runbook",
    "firestop-precover-gate",
    "damper-life-safety-gate",
    "shaft-inspection-gate",
    "pressure-test-gate",
    "inwall-cover-release",
    "mep-closeout",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status == "FAIL" and g.agent != "mep-lead" for g in active):
        return "HOLD"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next MEP sequence / workflow", "Maintain firestop photos + test logs"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — do not cover / energize / enter uncontrolled shafts",
            "Preserve photos, UL tags, pressure charts, timestamps",
            "Re-enter through pre-mep-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "mep-lead"]
    return [
        "Do not cover walls/ceilings or backfill shafts",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.clash = ClashCoordAgent()
        self.sleeves = SleevePenetrationAgent()
        self.hvac = HvacRoughAgent()
        self.elec = ElectricalRoughAgent()
        self.plum = PlumbingRoughAgent()
        self.fire = FirestopAgent()
        self.dampers = DamperLifeSafetyAgent()
        self.shaft = ShaftAccessAgent()
        self.pressure = PressureTestAgent()
        self.insul = InsulationHangersAgent()
        self.labels = LabelingAsbuiltAgent()
        self.weather = WeatherGateAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = MepLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_mep_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.clash.evaluate(ctx),
            self.sleeves.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-mep-gate", ctx, gates, {
            "GO": "Pre-MEP clear — rough-in may begin.",
            "HOLD": "Pre-MEP holding — clash/sleeves/crew.",
            "ABORT": "Pre-MEP aborted by fail-safe.",
        })

    def clash_sleeve_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.clash.evaluate(ctx), self.sleeves.evaluate(ctx), self.qa.evaluate(ctx, phase="pre"), self.safety.evaluate(ctx)]
        return self._finish("clash-sleeve-gate", ctx, gates, {
            "GO": "Clash/sleeve gate clear.",
            "HOLD": "Clash/sleeve holding.",
            "ABORT": "Clash/sleeve aborted.",
        })

    def hvac_rough_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.hvac.evaluate({**ctx, "require_hvac": True}),
            self.insul.evaluate(ctx),
            self.dampers.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("hvac-rough-runbook", ctx, gates, {
            "GO": "HVAC rough clear.",
            "HOLD": "HVAC rough holding.",
            "ABORT": "HVAC aborted.",
        })

    def electrical_rough_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.elec.evaluate({**ctx, "require_electrical": True}),
            self.labels.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("electrical-rough-runbook", ctx, gates, {
            "GO": "Electrical rough clear.",
            "HOLD": "Electrical holding.",
            "ABORT": "Electrical aborted.",
        })

    def plumbing_rough_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.plum.evaluate({**ctx, "require_plumbing": True}),
            self.pressure.evaluate(ctx),
            self.insul.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("plumbing-rough-runbook", ctx, gates, {
            "GO": "Plumbing rough clear.",
            "HOLD": "Plumbing holding.",
            "ABORT": "Plumbing aborted.",
        })

    def firestop_precover_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.fire.evaluate(ctx),
            self.sleeves.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("firestop-precover-gate", ctx, gates, {
            "GO": "Firestop pre-cover clear.",
            "HOLD": "Firestop holding — no cover.",
            "ABORT": "Firestop aborted.",
        })

    def damper_life_safety_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.dampers.evaluate({**ctx, "require_dampers": True}),
            self.hvac.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("damper-life-safety-gate", ctx, gates, {
            "GO": "Damper/life-safety clear.",
            "HOLD": "Dampers holding.",
            "ABORT": "Dampers aborted.",
        })

    def shaft_inspection_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.shaft.evaluate({**ctx, "require_shaft": True}),
            self.clash.evaluate(ctx),
            self.fire.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("shaft-inspection-gate", ctx, gates, {
            "GO": "Shaft inspection clear.",
            "HOLD": "Shaft holding.",
            "ABORT": "Shaft aborted.",
        })

    def pressure_test_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.pressure.evaluate(ctx),
            self.plum.evaluate(ctx),
            self.hvac.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
        ]
        return self._finish("pressure-test-gate", ctx, gates, {
            "GO": "Pressure/DALT tests clear.",
            "HOLD": "Pressure tests holding/failed.",
            "ABORT": "Pressure tests aborted.",
        })

    def inwall_cover_release(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.clash.evaluate(ctx),
            self.fire.evaluate(ctx),
            self.hvac.evaluate({**ctx, "require_hvac": True}),
            self.elec.evaluate({**ctx, "require_electrical": True}),
            self.plum.evaluate({**ctx, "require_plumbing": True}),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("inwall-cover-release", ctx, gates, {
            "GO": "In-wall cover released.",
            "HOLD": "Cover blocked — clash/firestop/trades.",
            "ABORT": "Cover release aborted.",
        })

    def mep_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="post"),
            self.fire.evaluate(ctx),
            self.pressure.evaluate(ctx),
            self.labels.evaluate(ctx),
            self.dampers.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("mep-closeout", ctx, gates, {
            "GO": "MEP closeout complete.",
            "HOLD": "MEP closeout incomplete.",
            "ABORT": "MEP closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        reason = ctx.get("block_reason") or "unspecified gate failure"
        severity = (ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        gates = [GateResult(
            "safety-failsafe" if decision == "ABORT" else "mep-lead",
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

    write(mod / "swarm.py", '''"""MEP rough-in + firestop swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.mep_swarm.schemas import SwarmResult
from modules.mep_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class MepSwarm:
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
        log_event(f"[mep-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[mep-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["MepSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.mep_swarm.swarm import MepSwarm, SwarmResult
from modules.mep_swarm.workflows import WORKFLOW_IDS

__all__ = ["MepSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for MEP rough-in + firestop swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.mep_swarm.swarm import MepSwarm

app = typer.Typer(add_completion=False, help="MEP rough-in + firestop swarm")


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
    for w in MepSwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = MepSwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "mep" / "fixtures" / "pre_mep_go.yaml"
    result = MepSwarm().run("pre-mep-gate", yaml.safe_load(fixture.read_text()))
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

from modules.mep_swarm.swarm import MepSwarm
from modules.mep_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = MepSwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[mep-swarm-api] {self.address_string()} {fmt % args}")

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
        if isinstance(payload.get("MepContextJson"), str):
            try:
                context = {**context, **json.loads(payload["MepContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "MepContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8084)
    args = p.parse_args()
    print(f"MEP swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-L2-ZONE-C
area: Level 2 Zone C
clash:
  resolved: true
  unresolved: []
  sleeve_map_published: true
sleeves:
  placed_per_map: true
  gross_offset: false
  missing_on_rated: []
hvac:
  seams_sealed: true
  hangers_ok: true
  dampers_incomplete: false
electrical:
  conduit_ok: true
  fill_ok: true
  panels_ok: true
  grounding_fail: false
  ir_fail: false
plumbing:
  layout_ok: true
  slope_ok: true
firestop:
  ul_matched: true
  photos_before_cover: true
  log_signed: true
  wrong_ul_system: false
  covered_without_inspection: false
dampers:
  installed: true
  accessible: true
  tagged: true
  actuation_required: true
  actuation_passed: true
shaft:
  trade_sequence_ok: true
  missing_access_hatch: false
  clearance_conflict: false
pressure_test:
  required: true
  performed: true
  passed: true
insulation:
  hangers_ok: true
  insulation_complete: true
labeling:
  critical_unlabeled: []
  redlines_current: true
weather:
  lightning: false
  wind_kph: 12
crew:
  roles:
    - mep_lead
    - hvac_tech
    - electrician
    - plumber
    - firestop_tech
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
"""
    write(agents_root / "fixtures" / "pre_mep_go.yaml", go)
    write(studio / "samples" / "pre_mep_go.yaml", go)
    write(agents_root / "fixtures" / "firestop_hold.yaml", """zone_id: DEMO-L2-ZONE-C
sleeves:
  placed_per_map: true
  missing_on_rated: []
firestop:
  ul_matched: false
  photos_before_cover: false
  log_signed: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "cover_without_firestop_abort.yaml", """zone_id: DEMO-L2-ZONE-C
clash:
  resolved: true
  sleeve_map_published: true
sleeves:
  placed_per_map: true
firestop:
  ul_matched: true
  photos_before_cover: false
  log_signed: false
  covered_without_inspection: true
hvac:
  seams_sealed: true
  hangers_ok: true
electrical:
  conduit_ok: true
  fill_ok: true
  panels_ok: true
plumbing:
  layout_ok: true
  slope_ok: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "pressure_test_fail.yaml", """zone_id: DEMO-L2-ZONE-C
pressure_test:
  required: true
  performed: true
  passed: false
  notes: 8 psi drop in 2 hours
plumbing:
  layout_ok: true
  slope_ok: true
hvac:
  seams_sealed: true
  hangers_ok: true
qa:
  install_hold_points_clear: true
""")
    write(agents_root / "fixtures" / "clash_hold.yaml", """zone_id: DEMO-L2-ZONE-C
clash:
  resolved: false
  unresolved: [duct-vs-beam-B12, pipe-vs-conduit-C3]
  sleeve_map_published: true
sleeves:
  placed_per_map: true
crew:
  roles: [mep_lead, hvac_tech, electrician, plumber, firestop_tech, qc_tech, safety_watch]
  briefing_complete: true
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")

    write(ROOT / "tests" / "test_mep_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.mep_swarm.swarm import MepSwarm
from modules.mep_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "mep" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(MepSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_mep_go():
    assert MepSwarm().run("pre-mep-gate", _load("pre_mep_go.yaml")).decision == "GO"


def test_clash_hold():
    assert MepSwarm().run("clash-sleeve-gate", _load("clash_hold.yaml")).decision == "HOLD"


def test_firestop_hold():
    assert MepSwarm().run("firestop-precover-gate", _load("firestop_hold.yaml")).decision == "HOLD"


def test_cover_without_firestop_abort():
    assert MepSwarm().run("inwall-cover-release", _load("cover_without_firestop_abort.yaml")).decision == "ABORT"


def test_pressure_fail_hold():
    r = MepSwarm().run("pressure-test-gate", _load("pressure_test_fail.yaml"))
    assert r.decision == "HOLD"


def test_hvac_go():
    assert MepSwarm().run("hvac-rough-runbook", _load("pre_mep_go.yaml")).decision == "GO"


def test_inwall_cover_go():
    assert MepSwarm().run("inwall-cover-release", _load("pre_mep_go.yaml")).decision == "GO"


def test_closeout_go():
    assert MepSwarm().run("mep-closeout", _load("pre_mep_go.yaml")).decision == "GO"


def test_hold_abort():
    assert MepSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "LOTO"}).decision == "ABORT"
''')

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "MepFirestop-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
