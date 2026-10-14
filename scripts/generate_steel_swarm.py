#!/usr/bin/env python3
"""Generate structural steel erection swarm (Studio pack + Python twin + fixtures)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("erect-lead", "ErectLead", "Owns steel erection sequence and final GO/HOLD/ABORT assembly.",
     """You own the **structural steel erection sequence** for each level/zone and assemble the final GO/HOLD/ABORT.

## Sequence pattern (typical — do not skip)
1. Confirm fab/mill certs + anchors/baseplates + crane + weather + crew + safety
2. Set temporary bracing / stability plan before releasing pieces
3. Erect columns → beams / girders per erection drawing piece marks
4. Bolting: snug-tight → final pretension (RCSC); welding per WPS/AWS D1.1
5. Establish stability / bracing lock-in before advancing
6. Plumb/alignment (AISC H/500 class) + decking release as scoped
7. QA hold points (torque logs, weld/NDT) cleared before advancing

Treat steel as prefabricated, sequenced, just-in-time — same discipline as mass timber/precast."""),
    ("fab-mill", "FabMill", "Owns shops, mill certs, heat numbers, and piece-mark deliveries.",
     """You own fabricator deliverables and mill certification.

## Required
- Approved shop / erection drawings with piece marks + sequence
- Mill certs / heat numbers match delivery tickets and piece marks
- Members free of damage, unacceptable rust, deformation
- Field bolt kits verified (grade, diameter, length, thread type)
- Fabrication inspection records available when required

HOLD if heat numbers, piece marks, or bolt kits do not match the next sequence."""),
    ("survey-anchors", "SurveyAnchors", "Owns anchor bolt survey, baseplates, leveling, and embeds.",
     """You own foundation interface survey for steel.

## Checks
- Anchor bolt layout vs baseplate holes (surveyed)
- Leveling plates / shims installed as designed
- Baseplate elevation / level within AISC / project tolerance
- Grout plan ready for post-erect (do not invent readings)

FAIL/HOLD out-of-tolerance anchors before first column pick."""),
    ("crane-logistics", "CraneLogistics", "Owns crane chart, pick plans, exclusion zones, and laydown.",
     """You own crane and steel logistics.

## Checks
- Crane chart / capacity for heaviest pick
- Pick points / lift plans verified
- Exclusion zone set; path clearance verified
- Trailer or laydown plan matches erection sequence
- No overload / tagline plan as required

HOLD if chart or exclusion zone incomplete."""),
    ("temp-bracing", "TempBracing", "Owns temporary bracing and stability during erection.",
     """You own temporary bracing / stability.

## Rules
- Bracing plan issued before loading beams on unbraced columns
- Diagonal / guy / temporary members installed per engineer before advancing
- Unstable frame without required braces => FAIL (stop picks)

Do not allow next level until stability lock-in is confirmed."""),
    ("bolting", "Bolting", "Owns RCSC bolting: snug-tight, pretension, DTIs, torque logs.",
     """You own high-strength bolting per RCSC / AISC.

## Checks
- Bolt kits matched to joints (ASTM grade, diameter)
- Snug-tight achieved before pretension
- Final pretension method: calibrated wrench, DTI, or turn-of-nut as specified
- Torque / tension log complete for sampled joints
- No bolt refusal / painted threads without remedy

HOLD incomplete patterns or missing tension evidence."""),
    ("welding", "Welding", "Owns AWS D1.1 field welding, WPS, preheat, and NDT.",
     """You own field welding QA (AWS D1.1).

## Checks
- Welder qualifications current for process/position
- WPS available; preheat per AWS D1.1 when required
- Visual inspection: no cracks; undercut within limits
- NDT (MT/UT/RT) complete where specified
- Weld size within -0 / +1/16" of design (or project)

FAIL cracked welds or missing required NDT."""),
    ("plumb-alignment", "PlumbAlignment", "Owns column plumbness, beam elevation, and frame tolerances.",
     """You own AISC / project geometric tolerances.

## Typical acceptance (override with project spec)
- Column plumbness ≈ H/500 max out-of-plumb
- Baseplate levelness within project tolerance
- Beam elevations / camber within ASTM A6 / shops

HOLD out-of-tolerance members before cladding / decking release."""),
    ("decking", "Decking", "Owns metal deck installation release and attachment QA.",
     """You own metal decking when in scope.

## Checks
- Supporting steel plumb/bolted/welded sufficiently for deck loads
- Deck type / gauge / attachment pattern per shops
- Openings / edge closures coordinated
- No decking on unstable or unsecured framing

SKIP if no deck scope."""),
    ("fireproofing", "Fireproofing", "Owns SFRM/intumescent sequencing relative to steel erection.",
     """You own fireproofing sequencing relative to erected steel.

## Checks
- Surface prep acceptable for SFRM / intumescent
- Connections / decking that must precede fireproofing are complete
- Thickness / density hold points planned (do not invent readings)

HOLD if prep or sequencing blocks coating."""),
    ("weather-gate", "WeatherGate", "Owns weather holds for lifts, bolting, and welding.",
     """You own weather holds for steel erection.

## Holds
- Wind above project pick limit
- Lightning / active storm
- Welding / coating weather limits without shelter
- Ice / snow on members creating slip or fit-up risk

Missing weather data => HOLD."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work authority for steel erection.",
     """Stop-work authority for structural steel erection.

## Immediate ABORT
- Unstable member without required temporary brace
- Crane overload / exclusion zone breach
- Fall protection failure on open steel
- Structural connection failure / cracked critical weld under load

SafetyFailsafe FAIL => parent Decision ABORT."""),
    ("crew-ops", "CrewOps", "Owns erector roles, fatigue, and shift briefing.",
     """You own steel erector crew readiness.

## Required roles (typical)
erect_lead, crane_operator, rigger, connector, welder (if weld scope),
brace_crew, qc_tech, safety_watch

HOLD missing roles, incomplete briefing, or fatigued critical workers."""),
    ("coatings", "Coatings", "Owns primer touch-up, galvanizing damage, and finish coatings.",
     """You own coatings / galvanizing protection during erection.

## Checks
- Shop primer / galvanizing damage logged
- Touch-up materials staged
- Final coating hold points not blocked by incomplete connections

HOLD if exposed damage without touch-up plan on architectural steel."""),
    ("qa-inspector", "QaInspector", "Owns field QC hold points, torque/weld logs, and NCRs.",
     """You own steel field QC evidence.

## Evidence
- Pre-erect hold points clear
- Bolt tension logs / weld inspection reports / NDT as required
- NCRs tracked with owner and reinspect

Missing QA evidence for the phase => HOLD."""),
    ("grout-baseplate", "GroutBaseplate", "Owns baseplate leveling and nonshrink grout release.",
     """You own baseplate grouting after alignment.

## Checks
- Columns plumbed and temporarily secured
- Baseplate elevation accepted
- Nonshrink grout materials / procedure approved
- Anchor nuts tightened per sequence before/after grout as specified

HOLD if alignment not accepted before permanent grout."""),
]

WORKFLOWS = [
    ("pre-erect-gate", ["fab-mill", "survey-anchors", "crane-logistics", "temp-bracing", "crew-ops", "weather-gate", "safety-failsafe", "qa-inspector"],
     "Pre-erect clear — steel picks may begin.", "Pre-erect holding.", "Pre-erect aborted."),
    ("delivery-piece-gate", ["fab-mill", "crane-logistics", "weather-gate", "safety-failsafe"],
     "Delivery clear — piece marks/heat numbers OK.", "Delivery holding.", "Delivery aborted."),
    ("anchor-baseplate-gate", ["survey-anchors", "grout-baseplate", "qa-inspector", "safety-failsafe"],
     "Anchors/baseplates released for columns.", "Anchor/baseplate holding.", "Anchor gate aborted."),
    ("level-erect-runbook", ["temp-bracing", "bolting", "welding", "plumb-alignment", "decking", "qa-inspector", "weather-gate", "safety-failsafe"],
     "Level erect clear — continue sequence.", "Level erect holding.", "Level erect aborted."),
    ("column-beam-pick", ["crane-logistics", "temp-bracing", "bolting", "plumb-alignment", "safety-failsafe"],
     "Column/beam pick clear.", "Pick holding.", "Pick aborted."),
    ("bolting-qa", ["bolting", "qa-inspector", "safety-failsafe"],
     "Bolting QA clear.", "Bolting holding.", "Bolting aborted."),
    ("welding-ndt-gate", ["welding", "qa-inspector", "weather-gate", "safety-failsafe"],
     "Welding/NDT clear.", "Welding holding.", "Welding aborted."),
    ("bracing-stability-lock", ["temp-bracing", "bolting", "qa-inspector", "safety-failsafe"],
     "Stability locked — level may advance.", "Stability not locked.", "Stability abort."),
    ("plumb-alignment-check", ["plumb-alignment", "survey-anchors", "qa-inspector"],
     "Plumb/alignment clear.", "Alignment holding.", "Alignment aborted."),
    ("decking-release", ["decking", "plumb-alignment", "bolting", "temp-bracing", "safety-failsafe"],
     "Decking released.", "Decking holding.", "Decking aborted."),
    ("level-closeout", ["qa-inspector", "bolting", "welding", "plumb-alignment", "coatings", "fireproofing", "crew-ops"],
     "Level closeout complete.", "Level closeout incomplete.", "Level closeout aborted."),
    ("hold-abort", [], "N/A", "HOLD escalated.", "ABORT escalated."),
]

ROLES = (
    "erect_lead", "crane_operator", "rigger", "connector",
    "brace_crew", "qc_tech", "safety_watch",
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip() if content.startswith("\n") else content)
    if not content.endswith("\n"):
        path.write_text(path.read_text() + "\n")


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
    Decision: GO | HOLD | ABORT. Prefer ErectContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: ErectContextJson
    description: JSON context for level/zone piece marks bolting welding crew
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    ErectContextJson:
      displayName: Erect Context JSON
      description: JSON context for steel erection
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
    agents_root = ROOT / "agents" / "steel"
    studio = ROOT / "copilot-studio" / "steel-crew"
    mod = ROOT / "modules" / "steel_swarm"

    # --- SOURCES / README ---
    write(agents_root / "SOURCES.md", """# Source basis for Structural Steel Erection Swarm

Primary field QA logic drawn from project `construction.md` extractions:

- QA/QC Field Procedures – Structural Steel Erection
- QA/QC Field Procedures – Structural Steel Construction (AISC / RCSC / AWS D1.1)

Aligned with AISC Code of Standard Practice, RCSC Specification for Structural Joints,
and AWS D1.1 for field welding / NDT hold points.
""")
    write(agents_root / "README.md", """# Structural Steel Erection Swarm (reference twin)

> **Primary runtime is Microsoft Copilot Studio.**  
> See [`../../copilot-studio/steel-crew/`](../../copilot-studio/steel-crew/) and open `START_HERE.md`.

```bash
python -m modules.steel_swarm.cli list
python -m modules.steel_swarm.cli run pre-erect-gate -c agents/steel/fixtures/pre_erect_go.yaml
python -m modules.steel_swarm.api --port 8082
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    write(agents_root / "instructions" / "root.md", """# Structural Steel Erection Swarm — Coordinator

You run **perfect, repeatable structural steel erection** for field crews. Return one GO / HOLD / ABORT with evidence.

## Specialists
| Agent | Owns |
| --- | --- |
| `erect-lead` | Level sequence, final decision |
| `fab-mill` | Shops, mill certs, heat numbers, piece marks |
| `survey-anchors` | Anchor bolts, baseplates, leveling |
| `crane-logistics` | Crane, picks, exclusion zones |
| `temp-bracing` | Temporary bracing / stability |
| `bolting` | RCSC snug / pretension / torque logs |
| `welding` | AWS D1.1 WPS / visual / NDT |
| `plumb-alignment` | AISC H/500 class geometry |
| `decking` | Metal deck release |
| `fireproofing` | SFRM / intumescent sequencing |
| `weather-gate` | Weather holds |
| `safety-failsafe` | Stop-work |
| `crew-ops` | Roles / briefing / fatigue |
| `coatings` | Primer / galvanizing touch-up |
| `qa-inspector` | Hold points / NCR |
| `grout-baseplate` | Baseplate grout release |

## Hard rules
1. Never erect without approved shops/erection drawings and matching mill certs / heat numbers.
2. Anchors/baseplates out of tolerance → HOLD before first column.
3. Temporary bracing before loading unbraced framing.
4. Pretension / weld-NDT evidence before closeout.
5. SafetyFailsafe FAIL → ABORT.
""")
    write(studio / "knowledge" / "files" / "root.md", (agents_root / "instructions" / "root.md").read_text())
    write(studio / "knowledge" / "files" / "SOURCES.md", (agents_root / "SOURCES.md").read_text())

    for wid, order, *_ in WORKFLOWS:
        body = f"# Workflow: `{wid}`\n\nGate order:\n"
        if order:
            body += "\n".join(f"{i+1}. `{a}`" for i, a in enumerate(order)) + "\n"
        else:
            body += "Escalation only — severity HOLD or ABORT with block_reason.\n"
        body += "\nParent assembles Decision from gates. SafetyFailsafe FAIL => ABORT.\n"
        write(agents_root / "workflows" / f"{wid}.md", body)
        write(studio / "knowledge" / "files" / f"{wid}.md", body)

    # Parent agent
    child_names = ", ".join(s[1] for s in SPECIALISTS)
    wf_ids = ", ".join(w[0] for w in WORKFLOWS)
    write(studio / "agent.mcs.yml", f"""mcs.metadata:
  componentName: SteelErectionSwarm
kind: GptComponentMetadata
displayName: Structural Steel Erection Swarm
instructions: |
  You are the Structural Steel Erection Swarm coordinator for field erection of
  structural steel (columns, beams, bracing, decking, bolted/welded connections).
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {child_names}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect ErectContextJson; missing critical fields => HOLD (do not invent readings).
  3. Invoke child agents IN DOCUMENTED ORDER for that workflow.
  4. Wait for Decision/Summary/GatesJson/ActionsJson from each child.
  5. One parent reply only. Children must not reply to the field user.
  6. SafetyFailsafe FAIL => final Decision ABORT.
  7. Align to AISC / RCSC / AWS D1.1 hold points from project construction QA extracts.

  ## Output shape
  WORKFLOW: <id>
  DECISION: GO | HOLD | ABORT
  SUMMARY: <2-4 sentences>
  GATES:
  - <agent>: PASS|FAIL|HOLD — <one line>
  ACTIONS:
  - <next field action>

  ## Workflow catalog
  {wf_ids}.

conversationStarters:
  - title: Pre-erect gate
    text: Run pre-erect-gate for Level 5 Grid A-D and return GO/HOLD/ABORT.
  - title: Delivery pieces
    text: Run delivery-piece-gate for the next steel truck against heat numbers and piece marks.
  - title: Level erect
    text: Run level-erect-runbook for today's column and beam picks.
  - title: Bolting QA
    text: Run bolting-qa — pretension logs for moment connections on Grid B.
  - title: Welding NDT
    text: Run welding-ndt-gate for CJP column splices before we release decking.
  - title: Decking release
    text: Run decking-release — is framing stable and plumbed enough for metal deck?

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: Structural Steel Erection Swarm
schemaName: steel_erectionSwarm
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
    write(studio / ".vscode" / "extensions.json", """{
  "recommendations": [
    "microsoft-IsvExpTools.powerplatform-vscode",
    "microsoft.copilotstudio-vscode",
    "redhat.vscode-yaml"
  ]
}
""")
    write(studio / "topics" / "Greeting.topic.mcs.yml", """kind: AdaptiveDialog
beginDialog:
  kind: OnConversationStart
  id: main
  actions:
    - kind: SendActivity
      id: sendGreeting
      activity:
        text:
          - Structural Steel Erection Swarm ready. Ask for pre-erect-gate, delivery-piece-gate, level-erect-runbook, bolting-qa, welding-ndt-gate, decking-release, or another named workflow. I return GO / HOLD / ABORT.
          - Steel erection online — share level/grid context and the gate to run.
""")
    write(studio / "actions" / "README.md", """# Actions

Wire Power Automate / MCP later to `python -m modules.steel_swarm.api` if desired.
""")
    write(studio / "README.md", """# Structural Steel Erection Swarm — Copilot Studio drop-in

Open **START_HERE.md** first.

Field swarm for structural steel erection (AISC / RCSC / AWS D1.1),
built the same way as the ConcreteOps and Mass Timber Copilot Studio packs.
""")
    write(studio / "START_HERE.md", """# START HERE — Structural Steel Erection Swarm drop-in

This folder is a **ready Copilot Studio agent workspace** for field steel erection.

## Sources
Project `construction.md` steel erection / steel construction QA extracts (AISC, RCSC, AWS D1.1). See `knowledge/files/SOURCES.md`.

## 3 steps

### 1) Open in VS Code
- Install **Microsoft Copilot Studio** VS Code extension (sign in to your work tenant).
- **File → Open Folder** → select this `steel-crew` folder (contains `agent.mcs.yml`).

### 2) Push to your environment
1. In Copilot Studio web: **Create** a blank agent named `Structural Steel Erection Swarm`.
2. In VS Code: **Clone agent** into a temp folder.
3. Copy **everything from this drop-in** over the clone (keep Studio `schemaName` if already assigned).
4. **Push** / sync.

### 3) Attach knowledge
1. Push parent + `agents/*` first.
2. Upload `knowledge/files/` as knowledge sources.
3. Test: *“Run pre-erect-gate for Level 5 Grid A-D…”*

## Named workflows
`pre-erect-gate`, `delivery-piece-gate`, `anchor-baseplate-gate`, `level-erect-runbook`, `column-beam-pick`, `bolting-qa`, `welding-ndt-gate`, `bracing-stability-lock`, `plumb-alignment-check`, `decking-release`, `level-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.steel_swarm.api --port 8082
python -m modules.steel_swarm.cli run pre-erect-gate -c agents/steel/fixtures/pre_erect_go.yaml
```
""")

    # --- Python twin ---
    write(mod / "schemas.py", '''from __future__ import annotations

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
    erect_id: str
    decision: Decision
    summary: str
    gates: list[GateResult]
    actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow,
            "erect_id": self.erect_id,
            "decision": self.decision,
            "summary": self.summary,
            "gates": [g.to_dict() for g in self.gates],
            "actions": list(self.actions),
        }

    def render(self) -> str:
        lines = [
            f"WORKFLOW: {self.workflow}",
            f"ERECT: {self.erect_id}",
            f"DECISION: {self.decision}",
            f"SUMMARY: {self.summary}",
            "GATES:",
        ]
        for g in self.gates:
            lines.append(f"- {g.agent}: {g.status} — {g.detail}")
        lines.append("ACTIONS:")
        for a in self.actions:
            lines.append(f"- {a}")
        return "\\n".join(lines)
''')

    agents_py = '''"""Deterministic specialist gates for structural steel erection."""

from __future__ import annotations

from typing import Any

from modules.steel_swarm.schemas import GateResult

DEFAULT_WIND_HOLD_KPH = 45.0
ERECT_ROLES = __ROLES__


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _missing_flags(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class FabMillAgent:
    name = "fab-mill"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("fab") or {}
        miss = _missing_flags(
            s,
            ("shops_approved", "erection_drawings_approved", "sequence_published", "mill_certs_matched"),
        )
        if miss:
            return GateResult(self.name, "HOLD", "Missing: " + ", ".join(miss), {"fab": s})
        truck = s.get("truck") or {}
        if truck:
            expected = set(truck.get("expected_piece_marks") or [])
            onboard = set(truck.get("onboard_piece_marks") or [])
            if expected and onboard != expected:
                return GateResult(
                    self.name,
                    "HOLD",
                    f"Piece marks mismatch expected={sorted(expected)} got={sorted(onboard)}",
                    {"truck": truck},
                )
            heats_ok = truck.get("heat_numbers_matched")
            if heats_ok is False:
                return GateResult(self.name, "HOLD", "Heat numbers do not match mill certs", {"truck": truck})
        if s.get("member_damage"):
            return GateResult(self.name, "HOLD", "Damaged/deformed members on delivery", {"fab": s})
        return GateResult(self.name, "PASS", "Fab/mill/piece marks ready", {"fab": s})


class SurveyAnchorsAgent:
    name = "survey-anchors"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("anchors") or {}
        if not a:
            return GateResult(self.name, "HOLD", "No anchor/baseplate survey package", {})
        if a.get("within_tolerance") is False:
            return GateResult(self.name, "FAIL", f"Anchors out of tolerance: {a.get('notes', 'see survey')}", {"anchors": a})
        miss = _missing_flags(a, ("layout_verified", "leveling_plates_set", "baseplate_elevation_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Anchor survey incomplete: " + ", ".join(miss), {"anchors": a})
        return GateResult(self.name, "PASS", "Anchors/baseplates within tolerance", {"anchors": a})


class CraneLogisticsAgent:
    name = "crane-logistics"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("crane") or {}
        miss = _missing_flags(c, ("chart_ok", "pick_plan_verified", "exclusion_zone_set"))
        if miss:
            return GateResult(self.name, "HOLD", "Crane logistics incomplete: " + ", ".join(miss), {"crane": c})
        if c.get("overload"):
            return GateResult(self.name, "FAIL", "Crane overload indicated", {"crane": c})
        return GateResult(self.name, "PASS", "Crane/logistics clear", {"crane": c})


class TempBracingAgent:
    name = "temp-bracing"

    def plan(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bracing") or {}
        if not b.get("plan_issued"):
            return GateResult(self.name, "HOLD", "Temporary bracing plan not issued", {"bracing": b})
        return GateResult(self.name, "PASS", "Temporary bracing plan issued", {"bracing": b})

    def lock_in(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bracing") or {}
        if b.get("unstable_without_brace"):
            return GateResult(self.name, "FAIL", "Unstable framing without required braces", {"bracing": b})
        if not b.get("braces_installed"):
            return GateResult(self.name, "HOLD", "Required temporary braces not installed", {"bracing": b})
        if not b.get("stability_locked"):
            return GateResult(self.name, "HOLD", "Stability not locked for advance", {"bracing": b})
        return GateResult(self.name, "PASS", "Bracing/stability locked", {"bracing": b})


class BoltingAgent:
    name = "bolting"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bolting") or {}
        if not b.get("kits_matched"):
            return GateResult(self.name, "HOLD", "Bolt kits not matched to joints", {"bolting": b})
        incomplete = list(b.get("incomplete_joints") or [])
        if incomplete:
            return GateResult(self.name, "HOLD", "Incomplete joints: " + ", ".join(incomplete), {"bolting": b})
        if b.get("pretension_required") and not b.get("tension_log_complete"):
            return GateResult(self.name, "HOLD", "Pretension/torque log incomplete", {"bolting": b})
        if b.get("structural_failure"):
            return GateResult(self.name, "FAIL", "Structural bolting failure reported", {"bolting": b})
        return GateResult(self.name, "PASS", "Bolting clear", {"bolting": b})


class WeldingAgent:
    name = "welding"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("welding") or {}
        if not w and not ctx.get("require_welding"):
            return GateResult(self.name, "SKIP", "No weld scope this gate", {})
        if w.get("required") is False:
            return GateResult(self.name, "PASS", "No field weld scope", {"welding": w})
        miss = _missing_flags(w, ("wps_available", "welders_qualified", "visual_accepted"))
        if miss:
            return GateResult(self.name, "HOLD", "Welding incomplete: " + ", ".join(miss), {"welding": w})
        if w.get("ndt_required") and not w.get("ndt_complete"):
            return GateResult(self.name, "HOLD", "Required NDT not complete", {"welding": w})
        if w.get("cracked_weld"):
            return GateResult(self.name, "FAIL", "Cracked weld reported — stop and repair per WPS", {"welding": w})
        return GateResult(self.name, "PASS", "Welding/NDT clear", {"welding": w})


class PlumbAlignmentAgent:
    name = "plumb-alignment"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("plumb") or {}
        if not p:
            return GateResult(self.name, "HOLD", "No plumb/alignment package", {})
        if p.get("within_tolerance") is False:
            return GateResult(self.name, "HOLD", f"Out of tolerance: {p.get('notes', 'see survey')}", {"plumb": p})
        if not p.get("columns_checked"):
            return GateResult(self.name, "HOLD", "Column plumb checks incomplete", {"plumb": p})
        return GateResult(self.name, "PASS", "Plumb/alignment within AISC/project tolerance", {"plumb": p})


class DeckingAgent:
    name = "decking"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("decking") or {}
        if not d and not ctx.get("require_decking"):
            return GateResult(self.name, "SKIP", "No decking scope", {})
        if d.get("required") is False:
            return GateResult(self.name, "PASS", "No decking this level", {"decking": d})
        if not d.get("framing_ready"):
            return GateResult(self.name, "HOLD", "Framing not ready for deck loads", {"decking": d})
        if not d.get("attachment_pattern_ok"):
            return GateResult(self.name, "HOLD", "Deck attachment pattern not confirmed", {"decking": d})
        return GateResult(self.name, "PASS", "Decking release clear", {"decking": d})


class FireproofingAgent:
    name = "fireproofing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("fireproofing") or {}
        if not f:
            return GateResult(self.name, "SKIP", "No fireproofing gate this workflow", {})
        if f.get("required") is False:
            return GateResult(self.name, "PASS", "No fireproofing this closeout", {"fireproofing": f})
        if not f.get("surface_prep_ok"):
            return GateResult(self.name, "HOLD", "Fireproofing surface prep not acceptable", {"fireproofing": f})
        if not f.get("sequencing_ok"):
            return GateResult(self.name, "HOLD", "Connections/decking sequencing blocks fireproofing", {"fireproofing": f})
        return GateResult(self.name, "PASS", "Fireproofing sequencing clear", {"fireproofing": f})


class CoatingsAgent:
    name = "coatings"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("coatings") or {}
        if not c:
            return GateResult(self.name, "SKIP", "No coatings scope", {})
        if c.get("damage") and not c.get("touchup_plan"):
            return GateResult(self.name, "HOLD", "Coating/galvanizing damage without touch-up plan", {"coatings": c})
        return GateResult(self.name, "PASS", "Coatings clear", {"coatings": c})


class GroutBaseplateAgent:
    name = "grout-baseplate"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("grout") or {}
        if g.get("required") is False:
            return GateResult(self.name, "PASS", "Grout not required this gate", {"grout": g})
        miss = _missing_flags(g, ("materials_approved", "alignment_accepted"))
        if miss:
            return GateResult(self.name, "HOLD", "Grout incomplete: " + ", ".join(miss), {"grout": g})
        return GateResult(self.name, "PASS", "Baseplate grout release clear", {"grout": g})


class WeatherGateAgent:
    name = "weather-gate"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        wind = _num(w.get("wind_kph"), 0) or 0
        limit = _num(w.get("wind_hold_kph"), DEFAULT_WIND_HOLD_KPH) or DEFAULT_WIND_HOLD_KPH
        holds: list[str] = []
        if wind >= limit:
            holds.append(f"wind {wind}kph ≥ {limit}kph")
        if w.get("lightning"):
            holds.append("lightning / storm active")
        if w.get("active_precip") and w.get("weld_exposed") and not w.get("shelter"):
            holds.append("precip on exposed weld without shelter")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", f"Weather CLEAR wind={wind}kph", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("bracing", {}).get("unstable_without_brace"):
            violations.append("unstable framing without brace")
        if ctx.get("crane", {}).get("overload"):
            violations.append("crane overload")
        if ctx.get("bolting", {}).get("structural_failure"):
            violations.append("structural bolting failure")
        if ctx.get("welding", {}).get("cracked_weld"):
            violations.append("cracked critical weld")
        if violations:
            return GateResult(self.name, "FAIL", "STOP-WORK: " + "; ".join(violations), {"violations": violations})
        return GateResult(self.name, "PASS", "No fail-safe violations", {})


class CrewOpsAgent:
    name = "crew-ops"

    def evaluate(self, ctx: dict[str, Any], require_briefing: bool = True) -> GateResult:
        crew = ctx.get("crew") or {}
        roles = set(crew.get("roles") or [])
        required = list(ERECT_ROLES)
        if (ctx.get("welding") or {}).get("required"):
            if "welder" not in roles:
                required.append("welder")
        missing = [r for r in required if r not in roles]
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
        checks = [c for c in (q.get("checks") or []) if c.get("phase", "pre") == phase]
        if not checks:
            if phase == "pre" and q.get("pre_hold_points_clear"):
                return GateResult(self.name, "PASS", "Pre-erect QA hold points clear", {})
            if phase != "pre" and q.get("pick_hold_points_clear"):
                return GateResult(self.name, "PASS", f"{phase} QA clear", {})
            return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})
        failed = [c for c in checks if not c.get("passed")]
        if failed:
            return GateResult(
                self.name,
                "FAIL",
                "QA failed: " + "; ".join(c.get("description", "check") for c in failed),
                {"failed": failed},
            )
        return GateResult(self.name, "PASS", f"QA {len(checks)} checks passed", {})


class ErectLeadAgent:
    name = "erect-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked erection"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('erect_id', ctx.get('level', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(
            self.name,
            status,
            f"{detail} [{hint}]",
            {"decision_hint": hint, "workflow": workflow, "level": ctx.get("level")},
        )
'''
    write(mod / "agents.py", agents_py.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named structural steel erection workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.steel_swarm.agents import (
    BoltingAgent,
    CoatingsAgent,
    CraneLogisticsAgent,
    CrewOpsAgent,
    DeckingAgent,
    ErectLeadAgent,
    FabMillAgent,
    FireproofingAgent,
    GroutBaseplateAgent,
    PlumbAlignmentAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SurveyAnchorsAgent,
    TempBracingAgent,
    WeatherGateAgent,
    WeldingAgent,
)
from modules.steel_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-erect-gate",
    "delivery-piece-gate",
    "anchor-baseplate-gate",
    "level-erect-runbook",
    "column-beam-pick",
    "bolting-qa",
    "welding-ndt-gate",
    "bracing-stability-lock",
    "plumb-alignment-check",
    "decking-release",
    "level-closeout",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status == "FAIL" and g.agent != "erect-lead" for g in active):
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            return "ABORT"
        return "HOLD"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next sequenced pick / workflow", "Maintain bracing + QA logs"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP PICKS — secure unstable members",
            "Preserve piece marks, torque/weld logs, photos, timestamps",
            "Re-enter only through pre-erect-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "erect-lead"]
    return [
        "Do not advance erection sequence",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("erect_id") or ctx.get("level") or "ERECT-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.fab = FabMillAgent()
        self.anchors = SurveyAnchorsAgent()
        self.crane = CraneLogisticsAgent()
        self.bracing = TempBracingAgent()
        self.bolting = BoltingAgent()
        self.welding = WeldingAgent()
        self.plumb = PlumbAlignmentAgent()
        self.decking = DeckingAgent()
        self.fire = FireproofingAgent()
        self.coatings = CoatingsAgent()
        self.grout = GroutBaseplateAgent()
        self.weather = WeatherGateAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = ErectLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        if any(g.status == "FAIL" and g.agent != "safety-failsafe" for g in gates):
            for g in gates:
                if g.status == "FAIL" and g.agent in {"temp-bracing", "bolting", "welding", "survey-anchors"}:
                    if not any(x.agent == "safety-failsafe" and x.status == "FAIL" for x in gates):
                        gates.append(GateResult("safety-failsafe", "FAIL", g.detail, g.evidence))
                    break
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_erect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.fab.evaluate(ctx),
            self.anchors.evaluate(ctx),
            self.crane.evaluate(ctx),
            self.bracing.plan(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish(
            "pre-erect-gate",
            ctx,
            gates,
            {
                "GO": "Pre-erect clear — steel picks may begin.",
                "HOLD": "Pre-erect holding — clear fab/anchors/crane/bracing/crew.",
                "ABORT": "Pre-erect aborted by fail-safe.",
            },
        )

    def delivery_piece_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.fab.evaluate(ctx),
            self.crane.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "delivery-piece-gate",
            ctx,
            gates,
            {
                "GO": "Delivery clear — piece marks/heat numbers OK.",
                "HOLD": "Delivery holding — piece marks/heat numbers/logistics.",
                "ABORT": "Delivery aborted by fail-safe.",
            },
        )

    def anchor_baseplate_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.anchors.evaluate(ctx),
            self.grout.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "anchor-baseplate-gate",
            ctx,
            gates,
            {
                "GO": "Anchors/baseplates released for columns.",
                "HOLD": "Anchor/baseplate holding.",
                "ABORT": "Anchor gate aborted.",
            },
        )

    def level_erect_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        if not ctx.get("pre_erect_go"):
            pre = self.pre_erect_gate(ctx)
            if pre.decision != "GO":
                pre.workflow = "level-erect-runbook"
                pre.summary = "Level erect blocked — pre-erect gate is not GO."
                return pre
        gates = [
            self.bracing.lock_in(ctx) if (ctx.get("bracing") or {}).get("braces_installed") is not None else self.bracing.plan(ctx),
            self.bolting.evaluate(ctx),
            self.welding.evaluate(ctx),
            self.plumb.evaluate(ctx),
            self.decking.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "level-erect-runbook",
            ctx,
            gates,
            {
                "GO": "Level erect clear — continue sequence.",
                "HOLD": "Level erect holding — braces/bolts/welds/plumb.",
                "ABORT": "Level erect aborted — stop picks and secure.",
            },
        )

    def column_beam_pick(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.crane.evaluate(ctx),
            self.bracing.plan(ctx),
            self.bolting.evaluate(ctx),
            self.plumb.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "column-beam-pick",
            ctx,
            gates,
            {
                "GO": "Column/beam pick clear.",
                "HOLD": "Pick holding.",
                "ABORT": "Pick aborted.",
            },
        )

    def bolting_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.bolting.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "bolting-qa",
            ctx,
            gates,
            {
                "GO": "Bolting QA clear.",
                "HOLD": "Bolting holding.",
                "ABORT": "Bolting aborted.",
            },
        )

    def welding_ndt_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.welding.evaluate({**ctx, "require_welding": True}),
            self.qa.evaluate(ctx, phase="during"),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "welding-ndt-gate",
            ctx,
            gates,
            {
                "GO": "Welding/NDT clear.",
                "HOLD": "Welding holding.",
                "ABORT": "Welding aborted.",
            },
        )

    def bracing_stability_lock(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.bracing.lock_in(ctx),
            self.bolting.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "bracing-stability-lock",
            ctx,
            gates,
            {
                "GO": "Stability locked — level may advance.",
                "HOLD": "Stability not locked.",
                "ABORT": "Stability abort — unstable frame.",
            },
        )

    def plumb_alignment_check(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.plumb.evaluate(ctx),
            self.anchors.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish(
            "plumb-alignment-check",
            ctx,
            gates,
            {
                "GO": "Plumb/alignment clear.",
                "HOLD": "Alignment holding.",
                "ABORT": "Alignment aborted.",
            },
        )

    def decking_release(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.decking.evaluate({**ctx, "require_decking": True}),
            self.plumb.evaluate(ctx),
            self.bolting.evaluate(ctx),
            self.bracing.lock_in(ctx) if (ctx.get("bracing") or {}).get("braces_installed") is not None else self.bracing.plan(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish(
            "decking-release",
            ctx,
            gates,
            {
                "GO": "Decking released.",
                "HOLD": "Decking holding.",
                "ABORT": "Decking aborted.",
            },
        )

    def level_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="post"),
            self.bolting.evaluate(ctx),
            self.welding.evaluate(ctx),
            self.plumb.evaluate(ctx),
            self.coatings.evaluate(ctx),
            self.fire.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish(
            "level-closeout",
            ctx,
            gates,
            {
                "GO": "Level closeout complete.",
                "HOLD": "Level closeout incomplete.",
                "ABORT": "Level closeout aborted.",
            },
        )

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        reason = ctx.get("block_reason") or "unspecified gate failure"
        severity = (ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        gates = [
            GateResult(
                "safety-failsafe" if decision == "ABORT" else "erect-lead",
                "FAIL" if decision == "ABORT" else "HOLD",
                reason,
                {"owner": ctx.get("owner", "superintendent")},
            )
        ]
        summary = (
            "ABORT escalated — stop picks and secure."
            if decision == "ABORT"
            else "HOLD escalated — clear owner action then re-check."
        )
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


RunnerFn = Callable[[dict[str, Any]], SwarmResult]


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, RunnerFn]:
    r = runner or WorkflowRunner()
    return {
        "pre-erect-gate": r.pre_erect_gate,
        "delivery-piece-gate": r.delivery_piece_gate,
        "anchor-baseplate-gate": r.anchor_baseplate_gate,
        "level-erect-runbook": r.level_erect_runbook,
        "column-beam-pick": r.column_beam_pick,
        "bolting-qa": r.bolting_qa,
        "welding-ndt-gate": r.welding_ndt_gate,
        "bracing-stability-lock": r.bracing_stability_lock,
        "plumb-alignment-check": r.plumb_alignment_check,
        "decking-release": r.decking_release,
        "level-closeout": r.level_closeout,
        "hold-abort": r.hold_abort,
    }
''')

    write(mod / "swarm.py", '''"""Structural steel erection swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.steel_swarm.schemas import SwarmResult
from modules.steel_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class SteelSwarm:
    """Deterministic swarm twin for Copilot Studio steel erection."""

    def __init__(self, runner: WorkflowRunner | None = None) -> None:
        self.runner = runner or WorkflowRunner()
        self.handlers = get_workflow_handlers(self.runner)

    def list_workflows(self) -> list[str]:
        return list(WORKFLOW_IDS)

    def run(self, workflow: str, context: dict[str, Any] | None = None) -> SwarmResult:
        if workflow not in self.handlers:
            known = ", ".join(WORKFLOW_IDS)
            raise ValueError(f"Unknown workflow '{workflow}'. Known: {known}")
        ctx = dict(context or {})
        ctx.setdefault("erect_id", "ERECT-UNSET")
        log_event(f"[steel-swarm] starting workflow={workflow} erect={ctx['erect_id']}")
        result = self.handlers[workflow](ctx)
        log_event(
            f"[steel-swarm] finished workflow={result.workflow} "
            f"erect={result.erect_id} decision={result.decision}"
        )
        return result


__all__ = ["SteelSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')

    write(mod / "__init__.py", '''"""Structural steel erection swarm — AISC/RCSC/AWS field workflows."""

from modules.steel_swarm.swarm import SteelSwarm, SwarmResult
from modules.steel_swarm.workflows import WORKFLOW_IDS

__all__ = ["SteelSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')

    write(mod / "cli.py", '''"""CLI for structural steel erection swarm workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.steel_swarm.swarm import SteelSwarm

app = typer.Typer(add_completion=False, help="Structural steel erection swarm")


def _load_context(path: Optional[Path]) -> dict:
    if path is None:
        return {}
    text = path.read_text()
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(text) or {}
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise typer.BadParameter("Context file must contain a JSON/YAML object")
    return data


@app.command("list")
def list_workflows() -> None:
    for workflow_id in SteelSwarm().list_workflows():
        print(f"- {workflow_id}")


@app.command("run")
def run_workflow(
    workflow: str = typer.Argument(...),
    context_file: Optional[Path] = typer.Option(None, "--context", "-c"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    result = SteelSwarm().run(workflow, _load_context(context_file))
    if as_json:
        print(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        print(result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo_pre_erect() -> None:
    from pathlib import Path
    import yaml

    fixture = Path(__file__).resolve().parents[2] / "agents" / "steel" / "fixtures" / "pre_erect_go.yaml"
    result = SteelSwarm().run("pre-erect-gate", yaml.safe_load(fixture.read_text()))
    print(result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


if __name__ == "__main__":
    app()
''')

    write(mod / "api.py", '''"""HTTP API for Copilot Studio / Power Automate connectors."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from modules.steel_swarm.swarm import SteelSwarm
from modules.steel_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = SteelSwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[steel-swarm-api] {self.address_string()} {fmt % args}")

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
        workflow_id = unquote(path[len(prefix) : -len("/run")].strip("/"))
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send(400, {"error": "invalid JSON"})
            return
        context = payload.get("context") or {}
        if isinstance(payload.get("ErectContextJson"), str):
            try:
                context = {**context, **json.loads(payload["ErectContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "ErectContextJson is not valid JSON"})
                return
        try:
            result = self.swarm.run(workflow_id, context)
        except ValueError as exc:
            self._send(400, {"error": str(exc)})
            return
        self._send(200, result.to_dict())


def main() -> None:
    parser = argparse.ArgumentParser(description="Steel swarm HTTP API for Copilot Studio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8082)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Steel swarm API on http://{args.host}:{args.port}")
    print(f"Workflows: {', '.join(WORKFLOW_IDS)}")
    server.serve_forever()


if __name__ == "__main__":
    main()
''')

    # Fixtures
    go = """erect_id: DEMO-L5-GRID-AD
level: Level 5 Grid A-D
pre_erect_go: true
fab:
  shops_approved: true
  erection_drawings_approved: true
  sequence_published: true
  mill_certs_matched: true
  member_damage: false
  truck:
    expected_piece_marks: [C-501, B-512, BR-5A]
    onboard_piece_marks: [C-501, B-512, BR-5A]
    heat_numbers_matched: true
anchors:
  within_tolerance: true
  layout_verified: true
  leveling_plates_set: true
  baseplate_elevation_ok: true
crane:
  chart_ok: true
  pick_plan_verified: true
  exclusion_zone_set: true
bracing:
  plan_issued: true
  braces_installed: true
  stability_locked: true
bolting:
  kits_matched: true
  incomplete_joints: []
  pretension_required: true
  tension_log_complete: true
welding:
  required: true
  wps_available: true
  welders_qualified: true
  visual_accepted: true
  ndt_required: true
  ndt_complete: true
  cracked_weld: false
plumb:
  within_tolerance: true
  columns_checked: true
decking:
  required: true
  framing_ready: true
  attachment_pattern_ok: true
fireproofing:
  required: true
  surface_prep_ok: true
  sequencing_ok: true
coatings:
  damage: false
  touchup_plan: true
grout:
  materials_approved: true
  alignment_accepted: true
weather:
  wind_kph: 20
  lightning: false
  active_precip: false
crew:
  roles:
    - erect_lead
    - crane_operator
    - rigger
    - connector
    - welder
    - brace_crew
    - qc_tech
    - safety_watch
  headcount: 12
  briefing_complete: true
  fatigued_workers: []
qa:
  pre_hold_points_clear: true
  pick_hold_points_clear: true
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_erect_go.yaml", go)
    write(studio / "samples" / "pre_erect_go.yaml", go)
    write(agents_root / "fixtures" / "delivery_heat_hold.yaml", """erect_id: DEMO-L5-TRUCK-03
fab:
  shops_approved: true
  erection_drawings_approved: true
  sequence_published: true
  mill_certs_matched: true
  truck:
    expected_piece_marks: [C-501, C-502, B-512]
    onboard_piece_marks: [C-501, B-512]
    heat_numbers_matched: false
crane:
  chart_ok: true
  pick_plan_verified: true
  exclusion_zone_set: true
weather:
  wind_kph: 15
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "bracing_abort.yaml", """erect_id: DEMO-L5-GRID-AD
bracing:
  plan_issued: true
  braces_installed: false
  stability_locked: false
  unstable_without_brace: true
bolting:
  kits_matched: true
  incomplete_joints: []
  pretension_required: false
  tension_log_complete: true
qa:
  pick_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "welding_ndt_hold.yaml", """erect_id: DEMO-L5-GRID-AD
welding:
  required: true
  wps_available: true
  welders_qualified: true
  visual_accepted: true
  ndt_required: true
  ndt_complete: false
  cracked_weld: false
weather:
  wind_kph: 12
  active_precip: false
qa:
  pick_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "bolting_torque_hold.yaml", """erect_id: DEMO-L5-GRID-AD
bolting:
  kits_matched: true
  incomplete_joints: [MJ-B12]
  pretension_required: true
  tension_log_complete: false
qa:
  pick_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "decking_release_go.yaml", go)

    write(ROOT / "tests" / "test_steel_swarm.py", '''from __future__ import annotations

from pathlib import Path

import yaml

from modules.steel_swarm.swarm import SteelSwarm
from modules.steel_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "steel" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_expected_workflows():
    assert set(SteelSwarm().list_workflows()) == set(WORKFLOW_IDS)
    assert len(WORKFLOW_IDS) == 12


def test_pre_erect_go():
    result = SteelSwarm().run("pre-erect-gate", _load("pre_erect_go.yaml"))
    assert result.decision == "GO"
    assert any(g.agent == "fab-mill" and g.status == "PASS" for g in result.gates)


def test_delivery_heat_hold():
    result = SteelSwarm().run("delivery-piece-gate", _load("delivery_heat_hold.yaml"))
    assert result.decision == "HOLD"


def test_level_erect_go():
    result = SteelSwarm().run("level-erect-runbook", _load("pre_erect_go.yaml"))
    assert result.decision == "GO"


def test_bolting_hold():
    result = SteelSwarm().run("bolting-qa", _load("bolting_torque_hold.yaml"))
    assert result.decision == "HOLD"


def test_welding_ndt_hold():
    result = SteelSwarm().run("welding-ndt-gate", _load("welding_ndt_hold.yaml"))
    assert result.decision == "HOLD"


def test_bracing_abort():
    result = SteelSwarm().run("bracing-stability-lock", _load("bracing_abort.yaml"))
    assert result.decision == "ABORT"


def test_decking_release_go():
    result = SteelSwarm().run("decking-release", _load("decking_release_go.yaml"))
    assert result.decision == "GO"


def test_level_closeout_go():
    result = SteelSwarm().run("level-closeout", _load("pre_erect_go.yaml"))
    assert result.decision == "GO"


def test_hold_abort():
    result = SteelSwarm().run("hold-abort", {"erect_id": "X", "severity": "ABORT", "block_reason": "fall protection"})
    assert result.decision == "ABORT"


def test_unknown_workflow():
    try:
        SteelSwarm().run("nope", {})
        assert False
    except ValueError as exc:
        assert "Unknown workflow" in str(exc)
''')

    # Zip
    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "SteelErection-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")
    print(f"Studio: {studio}")
    print(f"Module: {mod}")


if __name__ == "__main__":
    main()
