#!/usr/bin/env python3
"""Generate interiors / drywall / shafts field swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("interiors-lead", "InteriorsLead", "Owns interiors sequence and final GO/HOLD/ABORT.",
     """You own **interior framing / drywall / shafts** sequencing and assemble GO/HOLD/ABORT.

## Sequence pattern
1. Submittals: studs, board types, fire/STC assemblies
2. Layout: partitions, openings, ceiling heights
3. Metal stud framing + blocking/backing
4. Shaftwall / fire-rated assemblies before adjacent cover
5. In-wall MEP inspected → cover release
6. Board hang, tape/finish levels, openings/doors
7. Acoustics continuity (sealants, isolation)

Do not invent UL designs, STC ratings, or inspection sign-offs."""),
    ("materials-submittal", "MaterialsSubmittal", "Owns stud, board, and assembly submittals.",
     """You own interiors materials readiness.

## Checks
- Stud/track gauges approved
- Board types (reg/MR/Type X/C) match assemblies
- Fire-rated / STC assembly UL or tested designs approved
- Fasteners, sealants, insulation approved

HOLD missing approvals before framing or board."""),
    ("layout-control", "LayoutControl", "Owns partition layout, openings, and tolerances.",
     """You own interiors layout.

## Checks
- Control lines / laser layout for partitions
- Opening sizes/locations vs door schedule
- Ceiling height / head-of-wall control

HOLD missing layout or openings that conflict with MEP/structure."""),
    ("metal-stud-framing", "MetalStudFraming", "Owns stud spacing, plumb, and bracing.",
     """You own metal stud framing.

## Checks
- Stud spacing/gauge per shops
- Plumb/plane within tolerance
- Bridging/bracing; deflection track at heads when required
- Kickers / seismic as specified

HOLD out-of-tolerance framing before board."""),
    ("shaftwall", "Shaftwall", "Owns shaftwall CH-studs, liner, and continuity.",
     """You own shaftwall systems.

## Checks
- CH-studs / J-track per UL design
- Liner panels continuous; joints sealed as required
- Access panels / penetrations firestopped before close

HOLD incomplete shaftwall before adjacent finishes or shaft use."""),
    ("acoustics-stc", "AcousticsStc", "Owns STC assemblies, sealants, and flanking paths.",
     """You own acoustic partition performance.

## Checks
- Assembly matches specified STC design
- Acoustic sealant at perimeter / outlets
- Resilient channel / isolation as specified; no flanking shorts

HOLD missing seals or wrong assembly for rated STC walls."""),
    ("fire-rated-assemblies", "FireRatedAssemblies", "Owns fire-rated wall continuity and UL designs.",
     """You own fire-rated interior assemblies.

## Checks
- UL/GA design ID matches install
- Layer count, orientation, fastener pattern
- Head-of-wall / bottom-of-wall firestopping continuity
- Penetrations firestopped (coordinate MEP)

HOLD incomplete rated assembly before cover/inspection."""),
    ("blocking-backing", "BlockingBacking", "Owns in-wall blocking for fixtures and equipment.",
     """You own blocking/backing.

## Checks
- Blocking at millwork, grab bars, TV, equipment per shops
- Gauge/size adequate; fastened to structure/studs
- Documented before board cover

HOLD missing critical blocking before hang."""),
    ("board-hang", "BoardHang", "Owns gypsum hang, fasteners, and cutouts.",
     """You own board hanging.

## Checks
- Correct board type on each face
- Fastener spacing/pattern; screws set without fracture
- Cutouts neat; damage patched or replaced

HOLD wrong board type or damaged sheets left in place."""),
    ("taping-finish", "TapingFinish", "Owns joint finish levels and texture readiness.",
     """You own taping/finishing.

## Checks
- Finish level (0–5) matches room schedule
- Joints dry; no blisters/ridges beyond tolerance
- Primer/texture readiness when required

HOLD unfinished joints before paint or punch."""),
    ("openings-doors", "OpeningsDoors", "Owns door frames, hardware prep, and clearances.",
     """You own openings and door frames.

## Checks
- Frames plumb/square; throat matches wall thickness
- Fire-rated frames/labels where required
- Clearances for doors/hardware

HOLD misaligned or unlabeled rated frames."""),
    ("inwall-cover-release", "InwallCoverRelease", "Owns MEP in-wall inspection before board cover.",
     """You own in-wall cover release.

## Checks
- Rough-in inspected / signed (MEP + firestop photos)
- Blocking confirmed
- No open NCRs in wall cavity

HOLD cover before in-wall release."""),
    ("weather-protect", "WeatherProtect", "Owns moisture/temp holds for board and finish.",
     """You own environmental holds for drywall.

## Holds
- High humidity / wet building without dry-in
- Freeze risk for mud/compound
- Board stored wet or warped

HOLD wet conditions before hang/tape."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work for scaffold, fire-rated compromise, egress.",
     """You have stop-work authority. FAIL => swarm **ABORT**.

## Fail conditions
- Unsafe scaffold / lift / stilts
- Fire-rated shaft or exit enclosure compromised without protection
- Egress path blocked by materials staging
- Hot work without permit near finishes"""),
    ("crew-ops", "CrewOps", "Owns roles, briefing, and fatigue for interiors crews.",
     """You own crew readiness.

## Roles
interiors_lead, framer, hanger, taper, shaft_tech, qc_tech, safety_watch

HOLD missing roles, incomplete briefing, or fatigue risk."""),
    ("qa-inspector", "QaInspector", "Owns ITP hold points and rated-assembly evidence.",
     """You own interiors QA evidence.

## Checks
- Pre-frame / pre-cover hold points signed
- Fire/STC assembly photos and UL refs logged
- NCRs closed before finish/punch

HOLD missing ITP evidence."""),
]

WORKFLOWS = [
    "pre-interiors-gate",
    "layout-framing-gate",
    "metal-stud-runbook",
    "shaftwall-gate",
    "fire-rated-assembly-gate",
    "acoustics-stc-gate",
    "inwall-cover-release",
    "board-hang-runbook",
    "taping-finish-gate",
    "weather-protect-gate",
    "interiors-closeout",
    "hold-abort",
]

ROLES = (
    "interiors_lead",
    "framer",
    "hanger",
    "taper",
    "shaft_tech",
    "qc_tech",
    "safety_watch",
)

ORDERS = {
    "pre-interiors-gate": ["materials-submittal", "layout-control", "crew-ops", "weather-protect", "safety-failsafe", "qa-inspector"],
    "layout-framing-gate": ["layout-control", "openings-doors", "qa-inspector"],
    "metal-stud-runbook": ["metal-stud-framing", "blocking-backing", "layout-control", "qa-inspector", "safety-failsafe"],
    "shaftwall-gate": ["shaftwall", "fire-rated-assemblies", "safety-failsafe", "qa-inspector"],
    "fire-rated-assembly-gate": ["fire-rated-assemblies", "shaftwall", "openings-doors", "qa-inspector", "safety-failsafe"],
    "acoustics-stc-gate": ["acoustics-stc", "metal-stud-framing", "qa-inspector"],
    "inwall-cover-release": ["inwall-cover-release", "blocking-backing", "fire-rated-assemblies", "qa-inspector", "safety-failsafe"],
    "board-hang-runbook": ["inwall-cover-release", "board-hang", "materials-submittal", "weather-protect", "qa-inspector", "safety-failsafe"],
    "taping-finish-gate": ["taping-finish", "board-hang", "weather-protect", "qa-inspector"],
    "weather-protect-gate": ["weather-protect", "safety-failsafe"],
    "interiors-closeout": ["qa-inspector", "fire-rated-assemblies", "acoustics-stc", "taping-finish", "openings-doors", "crew-ops"],
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
    Decision: GO | HOLD | ABORT. Prefer InteriorsContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: InteriorsContextJson
    description: JSON context for interiors framing drywall shafts fire STC
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    InteriorsContextJson:
      displayName: Interiors Context JSON
      description: JSON context for interiors / drywall
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
    agents_root = ROOT / "agents" / "interiors"
    studio = ROOT / "copilot-studio" / "interiors-crew"
    mod = ROOT / "modules" / "interiors_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for Interiors / Drywall / Shafts Swarm

From project `construction.md` extractions and typical interiors ITP practice:

- QA/QC Field Procedures – Metal Stud Framing & Gypsum Assemblies
- Shaftwall / fire-rated partitions (UL designs, head-of-wall)
- Acoustic (STC) continuity and in-wall cover release before board
""")
    write(agents_root / "README.md", """# Interiors / Drywall / Shafts Swarm (reference twin)

> See [`../../copilot-studio/interiors-crew/`](../../copilot-studio/interiors-crew/) → `START_HERE.md`.

```bash
python -m modules.interiors_swarm.cli list
python -m modules.interiors_swarm.cli run pre-interiors-gate -c agents/interiors/fixtures/pre_interiors_go.yaml
python -m modules.interiors_swarm.api --port 8091
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# Interiors Swarm — Coordinator

Return one GO / HOLD / ABORT for framing / drywall / shafts.

## Hard rules
1. No board without materials + in-wall cover release.
2. Fire-rated / shaftwall assemblies must match UL design.
3. Blocking confirmed before hang at critical locations.
4. STC seals continuous where specified.
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
  componentName: InteriorsDrywallSwarm
kind: GptComponentMetadata
displayName: Interiors Drywall Swarm
instructions: |
  You are the Interiors / Drywall / Shafts Swarm coordinator.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect InteriorsContextJson; missing critical fields => HOLD (do not invent readings).
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
  - title: Pre-interiors gate
    text: Run pre-interiors-gate for Level 3 offices and return GO/HOLD/ABORT.
  - title: Metal stud runbook
    text: Run metal-stud-runbook for Corridor C walls.
  - title: Shaftwall
    text: Run shaftwall-gate for Elevator Shaft B.
  - title: In-wall cover release
    text: Run inwall-cover-release before we hang board on Grid D.
  - title: Fire-rated assembly
    text: Run fire-rated-assembly-gate for the 2-hour corridor.
  - title: Taping finish
    text: Run taping-finish-gate — Level 4 for paint?

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: Interiors Drywall Swarm
schemaName: interiors_drywall_swarm
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
          - Interiors Drywall Swarm ready. Ask for pre-interiors-gate, metal-stud-runbook, shaftwall-gate, inwall-cover-release, fire-rated-assembly-gate, or another named workflow. I return GO / HOLD / ABORT.
          - Interiors online — share floor/zone context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.interiors_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for interiors framing / drywall / shafts QA gates.\n")
    write(studio / "START_HERE.md", """# START HERE — Interiors Drywall Swarm drop-in

Ready Copilot Studio workspace for interiors / drywall / shafts field gates.

## 3 steps
1. Open this `interiors-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Interiors Drywall Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-interiors-gate…”*.

## Workflows
`pre-interiors-gate`, `layout-framing-gate`, `metal-stud-runbook`, `shaftwall-gate`, `fire-rated-assembly-gate`, `acoustics-stc-gate`, `inwall-cover-release`, `board-hang-runbook`, `taping-finish-gate`, `weather-protect-gate`, `interiors-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.interiors_swarm.api --port 8091
python -m modules.interiors_swarm.cli run pre-interiors-gate -c agents/interiors/fixtures/pre_interiors_go.yaml
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

    agents_src = r'''"""Deterministic specialist gates for interiors / drywall / shafts."""

from __future__ import annotations

from typing import Any

from modules.interiors_swarm.schemas import GateResult

ERECT_ROLES = __ROLES__


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class MaterialsSubmittalAgent:
    name = "materials-submittal"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("materials") or {}
        miss = _missing(m, ("studs_approved", "board_approved", "assemblies_approved"))
        if miss:
            return GateResult(self.name, "HOLD", "Materials incomplete: " + ", ".join(miss), {"materials": m})
        return GateResult(self.name, "PASS", "Stud/board/assembly submittals clear", {"materials": m})


class LayoutControlAgent:
    name = "layout-control"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("layout") or {}
        miss = _missing(l, ("control_lines", "openings_set"))
        if miss:
            return GateResult(self.name, "HOLD", "Layout incomplete: " + ", ".join(miss), {"layout": l})
        if l.get("conflicts"):
            return GateResult(self.name, "HOLD", "Layout conflicts: " + ", ".join(l["conflicts"]), {"layout": l})
        return GateResult(self.name, "PASS", "Layout/control clear", {"layout": l})


class MetalStudFramingAgent:
    name = "metal-stud-framing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("framing") or {}
        if f.get("spacing_ok") is False or f.get("gauge_ok") is False:
            return GateResult(self.name, "HOLD", "Stud spacing/gauge not per shops", {"framing": f})
        if f.get("plumb_ok") is False:
            return GateResult(self.name, "HOLD", "Framing plumb/plane out of tolerance", {"framing": f})
        if f.get("bracing_ok") is False:
            return GateResult(self.name, "HOLD", "Bridging/bracing/deflection track incomplete", {"framing": f})
        return GateResult(self.name, "PASS", "Metal stud framing clear", {"framing": f})


class ShaftwallAgent:
    name = "shaftwall"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("shaftwall") or {}
        if s.get("required") is False:
            return GateResult(self.name, "SKIP", "No shaftwall scope", {})
        if not s.get("ul_design_match"):
            return GateResult(self.name, "HOLD", "Shaftwall not matching UL design", {"shaftwall": s})
        if s.get("liner_continuous") is False:
            return GateResult(self.name, "HOLD", "Shaft liner not continuous/sealed", {"shaftwall": s})
        if s.get("penetrations_open"):
            return GateResult(self.name, "HOLD", "Shaft penetrations open before close", {"shaftwall": s})
        return GateResult(self.name, "PASS", "Shaftwall clear", {"shaftwall": s})


class AcousticsStcAgent:
    name = "acoustics-stc"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("acoustics") or {}
        if a.get("required") is False:
            return GateResult(self.name, "PASS", "STC not required this zone", {"acoustics": a})
        if not a.get("assembly_match"):
            return GateResult(self.name, "HOLD", "STC assembly does not match specified design", {"acoustics": a})
        if a.get("seals_ok") is False:
            return GateResult(self.name, "HOLD", "Acoustic seals incomplete", {"acoustics": a})
        if a.get("flanking"):
            return GateResult(self.name, "HOLD", "Flanking path shorts identified", {"acoustics": a})
        return GateResult(self.name, "PASS", "Acoustics/STC clear", {"acoustics": a})


class FireRatedAssembliesAgent:
    name = "fire-rated-assemblies"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("fire_rated") or {}
        if f.get("required") is False:
            return GateResult(self.name, "PASS", "No fire-rated assembly this gate", {"fire_rated": f})
        if not f.get("ul_design_match"):
            return GateResult(self.name, "HOLD", "Fire assembly UL/GA design mismatch", {"fire_rated": f})
        if f.get("layers_ok") is False or f.get("fastener_pattern_ok") is False:
            return GateResult(self.name, "HOLD", "Layer count/fastener pattern deficient", {"fire_rated": f})
        if f.get("head_of_wall_ok") is False:
            return GateResult(self.name, "HOLD", "Head-of-wall firestopping incomplete", {"fire_rated": f})
        if f.get("compromised"):
            return GateResult(self.name, "FAIL", "Fire-rated assembly compromised", {"fire_rated": f})
        return GateResult(self.name, "PASS", "Fire-rated assemblies clear", {"fire_rated": f})


class BlockingBackingAgent:
    name = "blocking-backing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("blocking") or {}
        if b.get("required") is False:
            return GateResult(self.name, "PASS", "No special blocking this gate", {"blocking": b})
        if b.get("missing"):
            return GateResult(self.name, "HOLD", "Missing blocking: " + ", ".join(b["missing"]), {"blocking": b})
        if not b.get("documented"):
            return GateResult(self.name, "HOLD", "Blocking not documented before cover", {"blocking": b})
        return GateResult(self.name, "PASS", "Blocking/backing clear", {"blocking": b})


class BoardHangAgent:
    name = "board-hang"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("board") or {}
        if b.get("type_ok") is False:
            return GateResult(self.name, "HOLD", "Wrong board type on assembly", {"board": b})
        if b.get("fasteners_ok") is False:
            return GateResult(self.name, "HOLD", "Fastener pattern/set deficient", {"board": b})
        if b.get("damaged_left"):
            return GateResult(self.name, "HOLD", "Damaged board left in place", {"board": b})
        return GateResult(self.name, "PASS", "Board hang clear", {"board": b})


class TapingFinishAgent:
    name = "taping-finish"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("finish") or {}
        if t.get("level_met") is False:
            return GateResult(self.name, "HOLD", f"Finish level not met (need {t.get('required_level', '?')})", {"finish": t})
        if t.get("defects"):
            return GateResult(self.name, "HOLD", "Finish defects: " + ", ".join(t["defects"]), {"finish": t})
        if not t.get("dry"):
            return GateResult(self.name, "HOLD", "Joints not dry for next coat/paint", {"finish": t})
        return GateResult(self.name, "PASS", "Taping/finish clear", {"finish": t})


class OpeningsDoorsAgent:
    name = "openings-doors"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        o = ctx.get("openings") or {}
        if o.get("required") is False:
            return GateResult(self.name, "SKIP", "No openings scope", {})
        if o.get("plumb_square") is False:
            return GateResult(self.name, "HOLD", "Frames not plumb/square", {"openings": o})
        if o.get("rated_unlabeled"):
            return GateResult(self.name, "HOLD", "Fire-rated frames unlabeled/mismatched", {"openings": o})
        return GateResult(self.name, "PASS", "Openings/doors clear", {"openings": o})


class InwallCoverReleaseAgent:
    name = "inwall-cover-release"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        i = ctx.get("inwall") or {}
        if not i.get("mep_signed"):
            return GateResult(self.name, "HOLD", "In-wall MEP inspection not signed", {"inwall": i})
        if not i.get("firestop_photos"):
            return GateResult(self.name, "HOLD", "Firestop photo log incomplete before cover", {"inwall": i})
        if i.get("open_ncrs"):
            return GateResult(self.name, "HOLD", "Open in-wall NCRs: " + ", ".join(i["open_ncrs"]), {"inwall": i})
        return GateResult(self.name, "PASS", "In-wall cover release clear", {"inwall": i})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No environmental data", {})
        holds = []
        if w.get("high_humidity") and not w.get("building_dry"):
            holds.append("high humidity / building not dry-in")
        if w.get("freezing") and not w.get("heat_for_mud"):
            holds.append("freeze risk for compound without heat")
        if w.get("wet_board_storage"):
            holds.append("board stored wet/warped")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Environment CLEAR", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("scaffold") or {}).get("unsafe"):
            violations.append("unsafe scaffold/lift/stilts")
        if (ctx.get("fire_rated") or {}).get("compromised"):
            violations.append("fire-rated shaft/assembly compromised")
        if (ctx.get("egress") or {}).get("blocked"):
            violations.append("egress path blocked by staging")
        if (ctx.get("hot_work") or {}).get("no_permit"):
            violations.append("hot work without permit")
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
            return GateResult(self.name, "PASS", "Pre-interiors QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class InteriorsLeadAgent:
    name = "interiors-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked interiors work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named interiors / drywall workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.interiors_swarm.agents import (
    AcousticsStcAgent,
    BlockingBackingAgent,
    BoardHangAgent,
    CrewOpsAgent,
    FireRatedAssembliesAgent,
    InteriorsLeadAgent,
    InwallCoverReleaseAgent,
    LayoutControlAgent,
    MaterialsSubmittalAgent,
    MetalStudFramingAgent,
    OpeningsDoorsAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    ShaftwallAgent,
    TapingFinishAgent,
    WeatherProtectAgent,
)
from modules.interiors_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-interiors-gate",
    "layout-framing-gate",
    "metal-stud-runbook",
    "shaftwall-gate",
    "fire-rated-assembly-gate",
    "acoustics-stc-gate",
    "inwall-cover-release",
    "board-hang-runbook",
    "taping-finish-gate",
    "weather-protect-gate",
    "interiors-closeout",
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
        return ["Proceed to next interiors sequence / workflow", "Keep UL/STC photos + in-wall release logs current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — secure scaffold; restore rated barriers / egress",
            "Preserve assembly photos, UL refs, timestamps",
            "Re-enter through pre-interiors-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "interiors-lead"]
    return [
        "Do not hang board / tape / close rated walls",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.materials = MaterialsSubmittalAgent()
        self.layout = LayoutControlAgent()
        self.framing = MetalStudFramingAgent()
        self.shaft = ShaftwallAgent()
        self.acoustics = AcousticsStcAgent()
        self.fire = FireRatedAssembliesAgent()
        self.blocking = BlockingBackingAgent()
        self.board = BoardHangAgent()
        self.finish = TapingFinishAgent()
        self.openings = OpeningsDoorsAgent()
        self.inwall = InwallCoverReleaseAgent()
        self.weather = WeatherProtectAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = InteriorsLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_interiors_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.materials.evaluate(ctx),
            self.layout.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-interiors-gate", ctx, gates, {
            "GO": "Pre-interiors clear — framing may proceed.",
            "HOLD": "Pre-interiors holding — materials/layout/environment.",
            "ABORT": "Pre-interiors aborted by fail-safe.",
        })

    def layout_framing_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.layout.evaluate(ctx), self.openings.evaluate(ctx), self.qa.evaluate(ctx, phase="pre")]
        return self._finish("layout-framing-gate", ctx, gates, {
            "GO": "Layout/framing control clear.",
            "HOLD": "Layout holding.",
            "ABORT": "Layout aborted.",
        })

    def metal_stud_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.framing.evaluate(ctx),
            self.blocking.evaluate(ctx),
            self.layout.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("metal-stud-runbook", ctx, gates, {
            "GO": "Metal stud framing clear.",
            "HOLD": "Metal stud holding.",
            "ABORT": "Metal stud aborted.",
        })

    def shaftwall_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "shaftwall": {**(ctx.get("shaftwall") or {}), "required": True},
               "fire_rated": {**(ctx.get("fire_rated") or {}), "required": True}}
        gates = [
            self.shaft.evaluate(ctx),
            self.fire.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("shaftwall-gate", ctx, gates, {
            "GO": "Shaftwall clear.",
            "HOLD": "Shaftwall holding.",
            "ABORT": "Shaftwall aborted — restore rated barrier.",
        })

    def fire_rated_assembly_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "fire_rated": {**(ctx.get("fire_rated") or {}), "required": True}}
        gates = [
            self.fire.evaluate(ctx),
            self.shaft.evaluate(ctx),
            self.openings.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("fire-rated-assembly-gate", ctx, gates, {
            "GO": "Fire-rated assembly clear.",
            "HOLD": "Fire-rated assembly holding.",
            "ABORT": "Fire-rated assembly aborted.",
        })

    def acoustics_stc_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "acoustics": {**(ctx.get("acoustics") or {}), "required": True}}
        gates = [
            self.acoustics.evaluate(ctx),
            self.framing.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("acoustics-stc-gate", ctx, gates, {
            "GO": "Acoustics/STC clear.",
            "HOLD": "Acoustics holding.",
            "ABORT": "Acoustics aborted.",
        })

    def inwall_cover_release(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.inwall.evaluate(ctx),
            self.blocking.evaluate(ctx),
            self.fire.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("inwall-cover-release", ctx, gates, {
            "GO": "In-wall cover release clear — board may hang.",
            "HOLD": "In-wall cover holding.",
            "ABORT": "In-wall cover aborted.",
        })

    def board_hang_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.inwall.evaluate(ctx),
            self.board.evaluate(ctx),
            self.materials.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("board-hang-runbook", ctx, gates, {
            "GO": "Board hang clear.",
            "HOLD": "Board hang holding.",
            "ABORT": "Board hang aborted.",
        })

    def taping_finish_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.finish.evaluate(ctx),
            self.board.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("taping-finish-gate", ctx, gates, {
            "GO": "Taping/finish clear.",
            "HOLD": "Taping/finish holding.",
            "ABORT": "Taping/finish aborted.",
        })

    def weather_protect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-protect-gate", ctx, gates, {
            "GO": "Environment clear.",
            "HOLD": "Environment holding.",
            "ABORT": "Environment aborted.",
        })

    def interiors_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="closeout"),
            self.fire.evaluate(ctx),
            self.acoustics.evaluate(ctx),
            self.finish.evaluate(ctx),
            self.openings.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("interiors-closeout", ctx, gates, {
            "GO": "Interiors closeout clear.",
            "HOLD": "Interiors closeout holding.",
            "ABORT": "Interiors closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "interiors-lead",
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

    write(mod / "swarm.py", '''"""Interiors / drywall swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.interiors_swarm.schemas import SwarmResult
from modules.interiors_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class InteriorsSwarm:
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
        log_event(f"[interiors-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[interiors-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["InteriorsSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.interiors_swarm.swarm import InteriorsSwarm, SwarmResult
from modules.interiors_swarm.workflows import WORKFLOW_IDS

__all__ = ["InteriorsSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for interiors / drywall swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.interiors_swarm.swarm import InteriorsSwarm

app = typer.Typer(add_completion=False, help="Interiors / drywall / shafts field swarm")


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
    for w in InteriorsSwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = InteriorsSwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "interiors" / "fixtures" / "pre_interiors_go.yaml"
    result = InteriorsSwarm().run("pre-interiors-gate", yaml.safe_load(fixture.read_text()))
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

from modules.interiors_swarm.swarm import InteriorsSwarm
from modules.interiors_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = InteriorsSwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[interiors-swarm-api] {self.address_string()} {fmt % args}")

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
        if isinstance(payload.get("InteriorsContextJson"), str):
            try:
                context = {**context, **json.loads(payload["InteriorsContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "InteriorsContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8091)
    args = p.parse_args()
    print(f"Interiors drywall swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-L3-OFFICES
area: Level 3 offices
materials:
  studs_approved: true
  board_approved: true
  assemblies_approved: true
layout:
  control_lines: true
  openings_set: true
  conflicts: []
framing:
  spacing_ok: true
  gauge_ok: true
  plumb_ok: true
  bracing_ok: true
shaftwall:
  required: true
  ul_design_match: true
  liner_continuous: true
  penetrations_open: false
acoustics:
  required: true
  assembly_match: true
  seals_ok: true
  flanking: false
fire_rated:
  required: true
  ul_design_match: true
  layers_ok: true
  fastener_pattern_ok: true
  head_of_wall_ok: true
  compromised: false
blocking:
  required: true
  missing: []
  documented: true
board:
  type_ok: true
  fasteners_ok: true
  damaged_left: false
finish:
  level_met: true
  required_level: 4
  defects: []
  dry: true
openings:
  required: true
  plumb_square: true
  rated_unlabeled: false
inwall:
  mep_signed: true
  firestop_photos: true
  open_ncrs: []
weather:
  high_humidity: false
  building_dry: true
  freezing: false
  heat_for_mud: true
  wet_board_storage: false
crew:
  roles:
    - interiors_lead
    - framer
    - hanger
    - taper
    - shaft_tech
    - qc_tech
    - safety_watch
  headcount: 12
  briefing_complete: true
  fatigued_workers: []
qa:
  pre_hold_points_clear: true
  install_hold_points_clear: true
scaffold:
  unsafe: false
egress:
  blocked: false
hot_work:
  no_permit: false
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_interiors_go.yaml", go)
    write(studio / "samples" / "pre_interiors_go.yaml", go)
    write(agents_root / "fixtures" / "no_cover_release_hold.yaml", """zone_id: DEMO-L3-OFFICES
inwall:
  mep_signed: false
  firestop_photos: false
  open_ncrs: [NCR-441]
blocking:
  required: true
  missing: [grab_bar_wet_wall]
  documented: false
fire_rated:
  required: true
  ul_design_match: true
  layers_ok: true
  fastener_pattern_ok: true
  head_of_wall_ok: true
  compromised: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "shaft_compromised_abort.yaml", """zone_id: DEMO-ELEV-SHAFT-B
shaftwall:
  required: true
  ul_design_match: false
  liner_continuous: false
  penetrations_open: true
fire_rated:
  required: true
  ul_design_match: false
  layers_ok: false
  fastener_pattern_ok: false
  head_of_wall_ok: false
  compromised: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "stc_flanking_hold.yaml", """zone_id: DEMO-L3-OFFICES
acoustics:
  required: true
  assembly_match: true
  seals_ok: false
  flanking: true
framing:
  spacing_ok: true
  gauge_ok: true
  plumb_ok: true
  bracing_ok: true
qa:
  install_hold_points_clear: true
""")
    write(agents_root / "fixtures" / "wet_board_hold.yaml", """zone_id: DEMO-L3-OFFICES
materials:
  studs_approved: true
  board_approved: true
  assemblies_approved: true
layout:
  control_lines: true
  openings_set: true
weather:
  high_humidity: true
  building_dry: false
  wet_board_storage: true
  freezing: false
crew:
  roles: [interiors_lead, framer, hanger, taper, shaft_tech, qc_tech, safety_watch]
  briefing_complete: true
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "scaffold_abort.yaml", """zone_id: DEMO-L3-OFFICES
scaffold:
  unsafe: true
egress:
  blocked: true
inwall:
  mep_signed: true
  firestop_photos: true
  open_ncrs: []
board:
  type_ok: true
  fasteners_ok: true
materials:
  studs_approved: true
  board_approved: true
  assemblies_approved: true
weather:
  high_humidity: false
  building_dry: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")

    write(ROOT / "tests" / "test_interiors_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.interiors_swarm.swarm import InteriorsSwarm
from modules.interiors_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "interiors" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(InteriorsSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_interiors_go():
    assert InteriorsSwarm().run("pre-interiors-gate", _load("pre_interiors_go.yaml")).decision == "GO"


def test_no_cover_release_hold():
    assert InteriorsSwarm().run("inwall-cover-release", _load("no_cover_release_hold.yaml")).decision == "HOLD"


def test_shaft_compromised_abort():
    assert InteriorsSwarm().run("shaftwall-gate", _load("shaft_compromised_abort.yaml")).decision == "ABORT"


def test_stc_flanking_hold():
    assert InteriorsSwarm().run("acoustics-stc-gate", _load("stc_flanking_hold.yaml")).decision == "HOLD"


def test_wet_board_hold():
    assert InteriorsSwarm().run("pre-interiors-gate", _load("wet_board_hold.yaml")).decision == "HOLD"


def test_scaffold_abort():
    assert InteriorsSwarm().run("board-hang-runbook", _load("scaffold_abort.yaml")).decision == "ABORT"


def test_board_hang_go():
    assert InteriorsSwarm().run("board-hang-runbook", _load("pre_interiors_go.yaml")).decision == "GO"


def test_closeout_go():
    assert InteriorsSwarm().run("interiors-closeout", _load("pre_interiors_go.yaml")).decision == "GO"


def test_hold_abort():
    assert InteriorsSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "egress"}).decision == "ABORT"
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

### Interiors / Drywall / Shafts Swarm (Copilot Studio)

Same pattern — field GO/HOLD/ABORT for framing, shaftwall, fire/STC, and board:

- [`copilot-studio/interiors-crew/`](copilot-studio/interiors-crew/) — parent + 16 child agents; open `START_HERE.md`
- Drop-in zip: [`packages/InteriorsDrywall-Swarm-CopilotStudio-DropIn.zip`](packages/InteriorsDrywall-Swarm-CopilotStudio-DropIn.zip)

```bash
python -m modules.interiors_swarm.api --port 8091
python -m modules.interiors_swarm.cli run pre-interiors-gate -c agents/interiors/fixtures/pre_interiors_go.yaml
```
"""
        if "Interiors / Drywall" not in rtxt and marker in rtxt:
            readme.write_text(rtxt.replace(marker, block + "\n", 1))

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "InteriorsDrywall-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
