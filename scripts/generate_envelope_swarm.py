#!/usr/bin/env python3
"""Generate envelope / waterproofing field swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("envelope-lead", "EnvelopeLead", "Owns envelope sequence and final GO/HOLD/ABORT.",
     """You own the **building envelope / waterproofing sequence** and assemble GO/HOLD/ABORT.

## Sequence pattern
1. Substrate ready (clean, dry, cured, slope) → WRB / air barrier continuity
2. Below-grade WP with protection/drainage before backfill
3. Roofing membrane: primer, laps, terminations, penetrations
4. Curtain wall / windows: setting blocks, sealants, water/air tests
5. Cladding / rainscreen without trapping moisture
6. Water test + air barrier verification before cover/closeout
7. QA photos + hold points cleared

Do not invent mil thickness, test pressures, or ambient readings."""),
    ("substrate-prep", "SubstratePrep", "Owns deck/wall/foundation substrate readiness.",
     """You own substrate readiness for membranes and WRB.

## Checks
- Deck/wall clean and dry
- Concrete cured per project (typical ≥7 days for below-grade WP)
- Voids/honeycombs patched; corners/transitions prepared
- Insulation flat with staggered joints where roofing
- Slope to drain verified (typical min 1/4\" per ft) when roofing

HOLD if wet, uncured, or out-of-slope substrate."""),
    ("weather-barrier", "WeatherBarrier", "Owns WRB / air barrier continuity and detailing.",
     """You own weather-resistive / air barrier continuity.

## Checks
- WRB / air barrier installed shingle-fashion
- Laps sealed; penetrations detailed
- Compatible with cladding and windows
- No bridging/wrinkles that break drainage plane
- Continuity at transitions (roof-to-wall, grade)

HOLD open WRB or missing transition detailing before cladding."""),
    ("below-grade-wp", "BelowGradeWp", "Owns below-grade sheet/liquid waterproofing.",
     """You own below-grade waterproofing.

## Checks
- Membrane type (sheet/liquid) per spec
- Laps sealed; no fishmouths, pinholes, blisters
- Wet-film / thickness evidence when liquid (≥ project mils)
- Transition membranes at corners
- Protection board + drainage mat before backfill

HOLD missing protection board before backfill."""),
    ("roofing-membrane", "RoofingMembrane", "Owns flat membrane roofing application QA.",
     """You own flat membrane roofing QA.

## Checks
- Primer per manufacturer; ambient within limits (often >40°F)
- Side laps / end laps per manufacturer (typical ≥3\" / ≥6\")
- Seam quality (rollers / torch / adhesive monitored)
- Daily seam pull tests when required
- Termination bars at parapets; penetrations flashed

HOLD incomplete seams or ambient out of range."""),
    ("flashing-penetrations", "FlashingPenetrations", "Owns flashings, boots, terminations, and parapets.",
     """You own flashings and penetrations.

## Checks
- Penetration flashing height per project (often >8\" above roof)
- Pipe boots sealed with approved method (not caulk-only)
- Step / head / valley flashing interweaved correctly
- Parapet / termination details complete
- Weeps not blocked by sealant

FAIL critical missing valley/eave ice-water where required."""),
    ("curtain-wall", "CurtainWall", "Owns curtain wall / window installation and performance tests.",
     """You own curtain wall and window QA.

## Checks
- Setting blocks continuous; glass bite per manufacturer
- Sealant / gasket continuous; field adhesion when required
- Anchorage / deflection within project (e.g. < L/175 class)
- Air (ASTM E283) / water (ASTM E331 / E1105) hold points scheduled
- No leakage at specified pressure/duration

HOLD incomplete perimeter seals before water test."""),
    ("cladding-rainscreen", "CladdingRainscreen", "Owns cladding and rainscreen drainage cavity QA.",
     """You own cladding / rainscreen.

## Checks
- WRB accepted before cladding
- Drainage cavity / furring clear; weeps open
- Fastener penetration into framing/blocking adequate
- Flashings at windows/heads integrated
- No trapped moisture paths

HOLD cladding over open WRB deficiencies."""),
    ("sealants", "Sealants", "Owns joint sealant prep, tooling, and adhesion.",
     """You own exterior sealants.

## Checks
- Joint prep clean/dry; backer rod / bond breaker correct
- Compatible sealant; tooled; full adhesion both sides
- Field adhesion test when specified (e.g. ASTM C794 class)
- Does not block weeps / drainage

HOLD failed adhesion or missing prep."""),
    ("water-test", "WaterTest", "Owns flood, ELD, and ASTM water penetration tests.",
     """You own water testing gates.

## Checks
- Method: flood test, ELD, hose, ASTM E331/E1105 as specified
- Test pressure / duration / acceptance criteria recorded
- Failures mapped with photos / locations
- Retest after repairs

HOLD if required water test not run before covering critical work.
FAIL active leakage beyond acceptance."""),
    ("air-barrier-test", "AirBarrierTest", "Owns blower-door / air leakage verification.",
     """You own air barrier testing.

## Checks
- Blower door / whole-building or mockup per project
- Target leakage (e.g. ≤0.4 cfm/sf @ 75 Pa class — use project)
- Leak paths mapped (smoke/IR) with owners
- Retest after remediation

HOLD missing required air test before enclosure closeout."""),
    ("drainage-protection", "DrainageProtection", "Owns slope-to-drain, protection board, and drainage mats.",
     """You own drainage and membrane protection.

## Checks
- Slope to drain verified for roofs
- Protection board / drainage composite installed before backfill or traffic
- Drains / scuppers clear and flashed
- No standing water trapped on membrane

HOLD unprotected membrane under backfill or traffic."""),
    ("weather-gate", "WeatherGate", "Owns ambient holds for membranes, sealants, and tests.",
     """You own weather holds for envelope work.

## Holds
- Ambient below manufacturer minimum (often 40°F membranes / 50°F sealants)
- Active precip on open substrate/membrane without approved shelter
- Wind above cladding / curtain-wall pick limits
- Surface moisture above manufacturer limits

Missing weather data => HOLD."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work authority for envelope / roofing work.",
     """Stop-work for envelope / roofing / WP.

## Immediate ABORT
- Fall protection failure on roof/edge
- Open hole / unprotected edge during roofing
- Hot-work / torch unsafe conditions
- Backfill against unprotected WP creating structural/water risk under load

SafetyFailsafe FAIL => parent Decision ABORT."""),
    ("crew-ops", "CrewOps", "Owns envelope crew roles, fatigue, and briefing.",
     """You own envelope crew readiness.

## Typical roles
envelope_lead, membrane_tech, flashing_tech, glazier (if CW),
sealant_tech, qc_tech, safety_watch

HOLD missing roles, incomplete briefing, or fatigued hot-work operators."""),
    ("qa-inspector", "QaInspector", "Owns envelope hold points, photos, and NCRs.",
     """You own envelope QC evidence.

## Evidence
- Pre-install hold points clear
- Seam pull tests, mil gauges, water/air test reports as required
- Photo log with locations
- NCRs with reinspect

Missing phase evidence => HOLD."""),
]

WORKFLOWS = [
    "pre-envelope-gate",
    "substrate-ready-gate",
    "wrb-air-barrier-gate",
    "below-grade-wp-runbook",
    "roofing-membrane-runbook",
    "flashing-penetration-qa",
    "curtain-wall-install-gate",
    "cladding-rainscreen-gate",
    "water-test-gate",
    "air-barrier-test-gate",
    "envelope-closeout",
    "hold-abort",
]

ROLES = (
    "envelope_lead",
    "membrane_tech",
    "flashing_tech",
    "sealant_tech",
    "qc_tech",
    "safety_watch",
)


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
    Decision: GO | HOLD | ABORT. Prefer EnvelopeContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: EnvelopeContextJson
    description: JSON context for envelope zone substrate membrane tests crew
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    EnvelopeContextJson:
      displayName: Envelope Context JSON
      description: JSON context for envelope / waterproofing
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
    agents_root = ROOT / "agents" / "envelope"
    studio = ROOT / "copilot-studio" / "envelope-crew"
    mod = ROOT / "modules" / "envelope_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for Envelope / Waterproofing Swarm

Primary field QA logic from project `construction.md` extractions:

- QA/QC Field Procedures – Roofing, Waterproofing & Envelope
- Building Envelope QA Workflow (final inspections)
- Roofing QAQC Field Logic, cladding/rainscreen, trim/flashing notes
- Curtain wall / window performance tests (ASTM E283 / E331 / E1105 class)
""")
    write(agents_root / "README.md", """# Envelope / Waterproofing Swarm (reference twin)

> **Primary runtime is Microsoft Copilot Studio.**  
> See [`../../copilot-studio/envelope-crew/`](../../copilot-studio/envelope-crew/) → `START_HERE.md`.

```bash
python -m modules.envelope_swarm.cli list
python -m modules.envelope_swarm.cli run pre-envelope-gate -c agents/envelope/fixtures/pre_envelope_go.yaml
python -m modules.envelope_swarm.api --port 8083
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root_md = """# Envelope / Waterproofing Swarm — Coordinator

You run **repeatable building envelope and waterproofing** field gates. Return one GO / HOLD / ABORT.

## Hard rules
1. Never cover WRB/membrane deficiencies.
2. No backfill without protection board + drainage on below-grade WP.
3. Water/air tests per project before closeout of critical assemblies.
4. SafetyFailsafe FAIL → ABORT.
5. Do not invent mils, pressures, or ambient readings.
"""
    write(agents_root / "instructions" / "root.md", root_md)
    write(studio / "knowledge" / "files" / "root.md", root_md)
    write(studio / "knowledge" / "files" / "SOURCES.md", (agents_root / "SOURCES.md").read_text())

    orders = {
        "pre-envelope-gate": ["substrate-prep", "weather-barrier", "crew-ops", "weather-gate", "safety-failsafe", "qa-inspector"],
        "substrate-ready-gate": ["substrate-prep", "drainage-protection", "weather-gate", "qa-inspector"],
        "wrb-air-barrier-gate": ["weather-barrier", "flashing-penetrations", "sealants", "qa-inspector", "safety-failsafe"],
        "below-grade-wp-runbook": ["substrate-prep", "below-grade-wp", "drainage-protection", "weather-gate", "qa-inspector", "safety-failsafe"],
        "roofing-membrane-runbook": ["substrate-prep", "roofing-membrane", "flashing-penetrations", "drainage-protection", "weather-gate", "qa-inspector", "safety-failsafe"],
        "flashing-penetration-qa": ["flashing-penetrations", "sealants", "qa-inspector"],
        "curtain-wall-install-gate": ["curtain-wall", "sealants", "weather-gate", "qa-inspector", "safety-failsafe"],
        "cladding-rainscreen-gate": ["weather-barrier", "cladding-rainscreen", "flashing-penetrations", "qa-inspector", "safety-failsafe"],
        "water-test-gate": ["water-test", "roofing-membrane", "curtain-wall", "qa-inspector", "safety-failsafe"],
        "air-barrier-test-gate": ["air-barrier-test", "weather-barrier", "sealants", "qa-inspector"],
        "envelope-closeout": ["qa-inspector", "water-test", "air-barrier-test", "cladding-rainscreen", "crew-ops"],
        "hold-abort": [],
    }
    for wid in WORKFLOWS:
        order = orders[wid]
        body = f"# Workflow: `{wid}`\n\nGate order:\n"
        body += ("\n".join(f"{i+1}. `{a}`" for i, a in enumerate(order)) + "\n") if order else "Escalation only.\n"
        body += "\nSafetyFailsafe FAIL => ABORT.\n"
        write(agents_root / "workflows" / f"{wid}.md", body)
        write(studio / "knowledge" / "files" / f"{wid}.md", body)

    children = ", ".join(s[1] for s in SPECIALISTS)
    write(studio / "agent.mcs.yml", f"""mcs.metadata:
  componentName: EnvelopeWaterproofingSwarm
kind: GptComponentMetadata
displayName: Envelope Waterproofing Swarm
instructions: |
  You are the Envelope / Waterproofing Swarm coordinator for field roofing,
  below-grade WP, WRB/air barrier, curtain wall, and cladding/rainscreen.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect EnvelopeContextJson; missing critical fields => HOLD (do not invent readings).
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
  - title: Pre-envelope gate
    text: Run pre-envelope-gate for Roof Area B and return GO/HOLD/ABORT.
  - title: Below-grade WP
    text: Run below-grade-wp-runbook before we backfill the east wall.
  - title: Roofing membrane
    text: Run roofing-membrane-runbook for today's TPO install.
  - title: Curtain wall
    text: Run curtain-wall-install-gate for Level 3 south elevation.
  - title: Water test
    text: Run water-test-gate after flashing repairs on Area A.
  - title: Air barrier
    text: Run air-barrier-test-gate — are we clear for enclosure closeout?

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: Envelope Waterproofing Swarm
schemaName: envelope_waterproofingSwarm
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
    write(studio / ".vscode" / "extensions.json", """{\n  "recommendations": [\n    "microsoft-IsvExpTools.powerplatform-vscode",\n    "microsoft.copilotstudio-vscode",\n    "redhat.vscode-yaml"\n  ]\n}\n""")
    write(studio / "topics" / "Greeting.topic.mcs.yml", """kind: AdaptiveDialog
beginDialog:
  kind: OnConversationStart
  id: main
  actions:
    - kind: SendActivity
      id: sendGreeting
      activity:
        text:
          - Envelope Waterproofing Swarm ready. Ask for pre-envelope-gate, below-grade-wp-runbook, roofing-membrane-runbook, water-test-gate, air-barrier-test-gate, or another named workflow. I return GO / HOLD / ABORT.
          - Envelope online — share zone context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.envelope_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for roofing, below-grade WP, WRB/air barrier, curtain wall, cladding.\n")
    write(studio / "START_HERE.md", """# START HERE — Envelope Waterproofing Swarm drop-in

Ready Copilot Studio workspace for field envelope / waterproofing.

## 3 steps
1. Open this `envelope-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Envelope Waterproofing Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-envelope-gate…”*.

## Workflows
`pre-envelope-gate`, `substrate-ready-gate`, `wrb-air-barrier-gate`, `below-grade-wp-runbook`, `roofing-membrane-runbook`, `flashing-penetration-qa`, `curtain-wall-install-gate`, `cladding-rainscreen-gate`, `water-test-gate`, `air-barrier-test-gate`, `envelope-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.envelope_swarm.api --port 8083
python -m modules.envelope_swarm.cli run pre-envelope-gate -c agents/envelope/fixtures/pre_envelope_go.yaml
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
        return "\\n".join(lines)
'''.replace("\\\\n", "\\n"))

    # Fix schemas render - write properly
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
        return "\\n".join(lines)
''')
    # The above still has escaped newline issue in join - fix with real write
    (mod / "schemas.py").write_text(
        (mod / "schemas.py").read_text().replace('return "\\\\n".join(lines)', 'return "\\n".join(lines)')
    )
    # Actually file has return "\n".join if we wrote \\n in triple quotes... let's just write agents and rest carefully

    agents_src = r'''"""Deterministic specialist gates for envelope / waterproofing."""

from __future__ import annotations

from typing import Any

from modules.envelope_swarm.schemas import GateResult

DEFAULT_MEMBRANE_MIN_F = 40.0
DEFAULT_WIND_HOLD_KPH = 50.0
ERECT_ROLES = __ROLES__


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class SubstratePrepAgent:
    name = "substrate-prep"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("substrate") or {}
        miss = _missing(s, ("clean", "dry"))
        if miss:
            return GateResult(self.name, "HOLD", "Substrate not ready: " + ", ".join(miss), {"substrate": s})
        if s.get("cured") is False:
            return GateResult(self.name, "HOLD", "Concrete/substrate not cured for membrane", {"substrate": s})
        if s.get("slope_ok") is False:
            return GateResult(self.name, "HOLD", "Slope to drain not verified", {"substrate": s})
        if s.get("voids_patched") is False:
            return GateResult(self.name, "HOLD", "Voids/honeycombs not patched", {"substrate": s})
        return GateResult(self.name, "PASS", "Substrate ready", {"substrate": s})


class WeatherBarrierAgent:
    name = "weather-barrier"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("wrb") or {}
        if not w and not ctx.get("require_wrb"):
            return GateResult(self.name, "SKIP", "No WRB scope", {})
        miss = _missing(w, ("installed", "laps_sealed", "transitions_detailed"))
        if miss:
            return GateResult(self.name, "HOLD", "WRB incomplete: " + ", ".join(miss), {"wrb": w})
        if w.get("open_deficiencies"):
            return GateResult(self.name, "HOLD", "Open WRB deficiencies: " + ", ".join(w["open_deficiencies"]), {"wrb": w})
        return GateResult(self.name, "PASS", "WRB/air barrier continuity clear", {"wrb": w})


class BelowGradeWpAgent:
    name = "below-grade-wp"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("below_grade") or {}
        if not b and not ctx.get("require_below_grade"):
            return GateResult(self.name, "SKIP", "No below-grade WP scope", {})
        miss = _missing(b, ("membrane_installed", "laps_sealed", "no_pinholes"))
        if miss:
            return GateResult(self.name, "HOLD", "Below-grade WP incomplete: " + ", ".join(miss), {"below_grade": b})
        mils = _num(b.get("wet_film_mils"))
        min_mils = _num(b.get("min_mils"), 60) or 60
        if mils is not None and mils < min_mils:
            return GateResult(self.name, "HOLD", f"Wet film {mils} mils < {min_mils}", {"below_grade": b})
        if not b.get("protection_board"):
            return GateResult(self.name, "HOLD", "Protection board/drainage not installed before backfill", {"below_grade": b})
        return GateResult(self.name, "PASS", "Below-grade WP clear", {"below_grade": b})


class RoofingMembraneAgent:
    name = "roofing-membrane"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        r = ctx.get("roofing") or {}
        if not r and not ctx.get("require_roofing"):
            return GateResult(self.name, "SKIP", "No roofing scope", {})
        miss = _missing(r, ("primer_ok", "laps_ok", "seams_accepted"))
        if miss:
            return GateResult(self.name, "HOLD", "Roofing incomplete: " + ", ".join(miss), {"roofing": r})
        if r.get("seam_pull_fail"):
            return GateResult(self.name, "FAIL", "Seam pull test failed", {"roofing": r})
        return GateResult(self.name, "PASS", "Roofing membrane clear", {"roofing": r})


class FlashingPenetrationsAgent:
    name = "flashing-penetrations"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("flashing") or {}
        miss = _missing(f, ("penetrations_flashed", "terminations_complete"))
        if miss:
            return GateResult(self.name, "HOLD", "Flashing incomplete: " + ", ".join(miss), {"flashing": f})
        if f.get("critical_missing"):
            return GateResult(self.name, "FAIL", "Critical flashing missing: " + ", ".join(f["critical_missing"]), {"flashing": f})
        return GateResult(self.name, "PASS", "Flashings/penetrations clear", {"flashing": f})


class CurtainWallAgent:
    name = "curtain-wall"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("curtain_wall") or {}
        if not c and not ctx.get("require_curtain_wall"):
            return GateResult(self.name, "SKIP", "No curtain wall scope", {})
        miss = _missing(c, ("setting_blocks_ok", "perimeter_sealed", "anchorage_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Curtain wall incomplete: " + ", ".join(miss), {"curtain_wall": c})
        return GateResult(self.name, "PASS", "Curtain wall install clear", {"curtain_wall": c})


class CladdingRainscreenAgent:
    name = "cladding-rainscreen"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("cladding") or {}
        if not c and not ctx.get("require_cladding"):
            return GateResult(self.name, "SKIP", "No cladding scope", {})
        if not c.get("wrb_accepted"):
            return GateResult(self.name, "HOLD", "WRB not accepted before cladding", {"cladding": c})
        miss = _missing(c, ("drainage_cavity_clear", "weeps_open", "flashings_integrated"))
        if miss:
            return GateResult(self.name, "HOLD", "Cladding incomplete: " + ", ".join(miss), {"cladding": c})
        return GateResult(self.name, "PASS", "Cladding/rainscreen clear", {"cladding": c})


class SealantsAgent:
    name = "sealants"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("sealants") or {}
        if not s:
            return GateResult(self.name, "SKIP", "No sealant scope", {})
        miss = _missing(s, ("joints_prepped", "tooled"))
        if miss:
            return GateResult(self.name, "HOLD", "Sealants incomplete: " + ", ".join(miss), {"sealants": s})
        if s.get("adhesion_fail"):
            return GateResult(self.name, "HOLD", "Sealant adhesion test failed", {"sealants": s})
        if s.get("weeps_blocked"):
            return GateResult(self.name, "HOLD", "Sealant blocking weeps/drainage", {"sealants": s})
        return GateResult(self.name, "PASS", "Sealants clear", {"sealants": s})


class WaterTestAgent:
    name = "water-test"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("water_test") or {}
        if t.get("required") is False:
            return GateResult(self.name, "PASS", "Water test not required this gate", {"water_test": t})
        if not t.get("performed"):
            return GateResult(self.name, "HOLD", "Required water test not performed", {"water_test": t})
        if t.get("passed") is False:
            return GateResult(self.name, "FAIL", f"Water test failed: {t.get('notes', 'leakage')}", {"water_test": t})
        return GateResult(self.name, "PASS", "Water test passed", {"water_test": t})


class AirBarrierTestAgent:
    name = "air-barrier-test"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("air_test") or {}
        if t.get("required") is False:
            return GateResult(self.name, "PASS", "Air test not required this gate", {"air_test": t})
        if not t.get("performed"):
            return GateResult(self.name, "HOLD", "Required air barrier test not performed", {"air_test": t})
        if t.get("passed") is False:
            return GateResult(self.name, "HOLD", f"Air leakage above target: {t.get('notes', 'see report')}", {"air_test": t})
        return GateResult(self.name, "PASS", "Air barrier test clear", {"air_test": t})


class DrainageProtectionAgent:
    name = "drainage-protection"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("drainage") or {}
        if not d:
            return GateResult(self.name, "SKIP", "No drainage/protection scope", {})
        if d.get("standing_water"):
            return GateResult(self.name, "HOLD", "Standing water on membrane", {"drainage": d})
        if d.get("requires_protection") and not d.get("protection_installed"):
            return GateResult(self.name, "HOLD", "Protection/drainage composite missing", {"drainage": d})
        if d.get("drains_clear") is False:
            return GateResult(self.name, "HOLD", "Drains/scuppers not clear/flashed", {"drainage": d})
        return GateResult(self.name, "PASS", "Drainage/protection clear", {"drainage": d})


class WeatherGateAgent:
    name = "weather-gate"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        temp = _num(w.get("temp_f"))
        min_f = _num(w.get("membrane_min_f"), DEFAULT_MEMBRANE_MIN_F) or DEFAULT_MEMBRANE_MIN_F
        wind = _num(w.get("wind_kph"), 0) or 0
        limit = _num(w.get("wind_hold_kph"), DEFAULT_WIND_HOLD_KPH) or DEFAULT_WIND_HOLD_KPH
        holds: list[str] = []
        if temp is not None and temp < min_f:
            holds.append(f"temp {temp}F < {min_f}F")
        if wind >= limit:
            holds.append(f"wind {wind}kph ≥ {limit}kph")
        if w.get("active_precip") and not w.get("shelter"):
            holds.append("active precip without shelter")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", f"Weather CLEAR temp={temp}F wind={wind}kph", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("roofing", {}).get("torch_unsafe"):
            violations.append("unsafe torch/hot-work conditions")
        if ctx.get("below_grade", {}).get("backfill_without_protection"):
            violations.append("backfill against unprotected waterproofing")
        if violations:
            return GateResult(self.name, "FAIL", "STOP-WORK: " + "; ".join(violations), {"violations": violations})
        return GateResult(self.name, "PASS", "No fail-safe violations", {})


class CrewOpsAgent:
    name = "crew-ops"

    def evaluate(self, ctx: dict[str, Any], require_briefing: bool = True) -> GateResult:
        crew = ctx.get("crew") or {}
        roles = set(crew.get("roles") or [])
        required = list(ERECT_ROLES)
        if (ctx.get("curtain_wall") or {}).get("required"):
            if "glazier" not in roles:
                required.append("glazier")
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
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-install QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        checks = [c for c in (q.get("checks") or []) if c.get("phase", "pre") == phase]
        if not checks:
            return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})
        failed = [c for c in checks if not c.get("passed")]
        if failed:
            return GateResult(self.name, "FAIL", "QA failed: " + "; ".join(c.get("description", "check") for c in failed), {"failed": failed})
        return GateResult(self.name, "PASS", f"QA {len(checks)} checks passed", {})


class EnvelopeLeadAgent:
    name = "envelope-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked envelope work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    # Fix schemas properly
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

    write(mod / "workflows.py", '''"""Named envelope / waterproofing workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.envelope_swarm.agents import (
    AirBarrierTestAgent,
    BelowGradeWpAgent,
    CladdingRainscreenAgent,
    CrewOpsAgent,
    CurtainWallAgent,
    DrainageProtectionAgent,
    EnvelopeLeadAgent,
    FlashingPenetrationsAgent,
    QaInspectorAgent,
    RoofingMembraneAgent,
    SafetyFailsafeAgent,
    SealantsAgent,
    SubstratePrepAgent,
    WaterTestAgent,
    WeatherBarrierAgent,
    WeatherGateAgent,
)
from modules.envelope_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-envelope-gate",
    "substrate-ready-gate",
    "wrb-air-barrier-gate",
    "below-grade-wp-runbook",
    "roofing-membrane-runbook",
    "flashing-penetration-qa",
    "curtain-wall-install-gate",
    "cladding-rainscreen-gate",
    "water-test-gate",
    "air-barrier-test-gate",
    "envelope-closeout",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status == "FAIL" and g.agent != "envelope-lead" for g in active):
        return "HOLD" if not any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active) else "ABORT"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next envelope sequence / workflow", "Maintain photo log + protection"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — secure open edges / hot-work / unprotected WP",
            "Preserve photos, test reports, timestamps",
            "Re-enter through pre-envelope-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "envelope-lead"]
    return [
        "Do not cover or backfill",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.substrate = SubstratePrepAgent()
        self.wrb = WeatherBarrierAgent()
        self.below = BelowGradeWpAgent()
        self.roof = RoofingMembraneAgent()
        self.flash = FlashingPenetrationsAgent()
        self.cw = CurtainWallAgent()
        self.clad = CladdingRainscreenAgent()
        self.seal = SealantsAgent()
        self.water = WaterTestAgent()
        self.air = AirBarrierTestAgent()
        self.drain = DrainageProtectionAgent()
        self.weather = WeatherGateAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = EnvelopeLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        if any(g.status == "FAIL" and g.agent in {"roofing-membrane", "flashing-penetrations", "water-test", "below-grade-wp"} for g in gates):
            if not any(x.agent == "safety-failsafe" and x.status == "FAIL" for x in gates):
                # structural water fails stay HOLD unless safety also trips; promote only backfill/torch via safety agent
                pass
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        # water-test FAIL should HOLD unless safety FAIL; _decide already maps non-safety FAIL to HOLD
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_envelope_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.substrate.evaluate(ctx),
            self.wrb.evaluate({**ctx, "require_wrb": bool(ctx.get("wrb"))}),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-envelope-gate", ctx, gates, {
            "GO": "Pre-envelope clear — membrane/WRB work may begin.",
            "HOLD": "Pre-envelope holding — substrate/WRB/crew/weather.",
            "ABORT": "Pre-envelope aborted by fail-safe.",
        })

    def substrate_ready_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.substrate.evaluate(ctx), self.drain.evaluate(ctx), self.weather.evaluate(ctx), self.qa.evaluate(ctx, phase="pre")]
        return self._finish("substrate-ready-gate", ctx, gates, {
            "GO": "Substrate ready for membrane/WRB.",
            "HOLD": "Substrate holding.",
            "ABORT": "Substrate aborted.",
        })

    def wrb_air_barrier_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.wrb.evaluate({**ctx, "require_wrb": True}),
            self.flash.evaluate(ctx),
            self.seal.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("wrb-air-barrier-gate", ctx, gates, {
            "GO": "WRB/air barrier clear.",
            "HOLD": "WRB/air barrier holding.",
            "ABORT": "WRB aborted.",
        })

    def below_grade_wp_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.substrate.evaluate(ctx),
            self.below.evaluate({**ctx, "require_below_grade": True}),
            self.drain.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("below-grade-wp-runbook", ctx, gates, {
            "GO": "Below-grade WP clear for protection/backfill sequence.",
            "HOLD": "Below-grade WP holding.",
            "ABORT": "Below-grade WP aborted.",
        })

    def roofing_membrane_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.substrate.evaluate(ctx),
            self.roof.evaluate({**ctx, "require_roofing": True}),
            self.flash.evaluate(ctx),
            self.drain.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("roofing-membrane-runbook", ctx, gates, {
            "GO": "Roofing membrane clear.",
            "HOLD": "Roofing holding.",
            "ABORT": "Roofing aborted.",
        })

    def flashing_penetration_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.flash.evaluate(ctx), self.seal.evaluate(ctx), self.qa.evaluate(ctx, phase="during")]
        return self._finish("flashing-penetration-qa", ctx, gates, {
            "GO": "Flashing/penetration QA clear.",
            "HOLD": "Flashing holding.",
            "ABORT": "Flashing aborted.",
        })

    def curtain_wall_install_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.cw.evaluate({**ctx, "require_curtain_wall": True}),
            self.seal.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("curtain-wall-install-gate", ctx, gates, {
            "GO": "Curtain wall install clear.",
            "HOLD": "Curtain wall holding.",
            "ABORT": "Curtain wall aborted.",
        })

    def cladding_rainscreen_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.wrb.evaluate({**ctx, "require_wrb": True}),
            self.clad.evaluate({**ctx, "require_cladding": True}),
            self.flash.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("cladding-rainscreen-gate", ctx, gates, {
            "GO": "Cladding/rainscreen clear.",
            "HOLD": "Cladding holding.",
            "ABORT": "Cladding aborted.",
        })

    def water_test_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.water.evaluate(ctx),
            self.roof.evaluate(ctx),
            self.cw.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("water-test-gate", ctx, gates, {
            "GO": "Water test clear.",
            "HOLD": "Water test holding / failed — repair and retest.",
            "ABORT": "Water test aborted.",
        })

    def air_barrier_test_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.air.evaluate(ctx),
            self.wrb.evaluate({**ctx, "require_wrb": True}),
            self.seal.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
        ]
        return self._finish("air-barrier-test-gate", ctx, gates, {
            "GO": "Air barrier test clear.",
            "HOLD": "Air barrier holding.",
            "ABORT": "Air barrier aborted.",
        })

    def envelope_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="post"),
            self.water.evaluate(ctx),
            self.air.evaluate(ctx),
            self.clad.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("envelope-closeout", ctx, gates, {
            "GO": "Envelope closeout complete.",
            "HOLD": "Envelope closeout incomplete.",
            "ABORT": "Envelope closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        reason = ctx.get("block_reason") or "unspecified gate failure"
        severity = (ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        gates = [GateResult(
            "safety-failsafe" if decision == "ABORT" else "envelope-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "superintendent")},
        )]
        summary = "ABORT escalated — stop work and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {
        "pre-envelope-gate": r.pre_envelope_gate,
        "substrate-ready-gate": r.substrate_ready_gate,
        "wrb-air-barrier-gate": r.wrb_air_barrier_gate,
        "below-grade-wp-runbook": r.below_grade_wp_runbook,
        "roofing-membrane-runbook": r.roofing_membrane_runbook,
        "flashing-penetration-qa": r.flashing_penetration_qa,
        "curtain-wall-install-gate": r.curtain_wall_install_gate,
        "cladding-rainscreen-gate": r.cladding_rainscreen_gate,
        "water-test-gate": r.water_test_gate,
        "air-barrier-test-gate": r.air_barrier_test_gate,
        "envelope-closeout": r.envelope_closeout,
        "hold-abort": r.hold_abort,
    }
''')

    write(mod / "swarm.py", '''"""Envelope / waterproofing swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.envelope_swarm.schemas import SwarmResult
from modules.envelope_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class EnvelopeSwarm:
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
        log_event(f"[envelope-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[envelope-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["EnvelopeSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.envelope_swarm.swarm import EnvelopeSwarm, SwarmResult
from modules.envelope_swarm.workflows import WORKFLOW_IDS

__all__ = ["EnvelopeSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for envelope / waterproofing swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.envelope_swarm.swarm import EnvelopeSwarm

app = typer.Typer(add_completion=False, help="Envelope / waterproofing swarm")


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
    for w in EnvelopeSwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = EnvelopeSwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "envelope" / "fixtures" / "pre_envelope_go.yaml"
    result = EnvelopeSwarm().run("pre-envelope-gate", yaml.safe_load(fixture.read_text()))
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

from modules.envelope_swarm.swarm import EnvelopeSwarm
from modules.envelope_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = EnvelopeSwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[envelope-swarm-api] {self.address_string()} {fmt % args}")

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        if path in ("/v1/workflows", "/v1/workflows/", "/health", "/v1/health"):
            self._send(200, {"workflows": list(WORKFLOW_IDS)} if "workflow" in path else {"ok": True})
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
        if isinstance(payload.get("EnvelopeContextJson"), str):
            try:
                context = {**context, **json.loads(payload["EnvelopeContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "EnvelopeContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8083)
    args = p.parse_args()
    print(f"Envelope swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-ROOF-B
area: Roof Area B
substrate:
  clean: true
  dry: true
  cured: true
  slope_ok: true
  voids_patched: true
wrb:
  installed: true
  laps_sealed: true
  transitions_detailed: true
  open_deficiencies: []
below_grade:
  membrane_installed: true
  laps_sealed: true
  no_pinholes: true
  wet_film_mils: 70
  min_mils: 60
  protection_board: true
roofing:
  primer_ok: true
  laps_ok: true
  seams_accepted: true
  seam_pull_fail: false
flashing:
  penetrations_flashed: true
  terminations_complete: true
  critical_missing: []
curtain_wall:
  required: true
  setting_blocks_ok: true
  perimeter_sealed: true
  anchorage_ok: true
cladding:
  wrb_accepted: true
  drainage_cavity_clear: true
  weeps_open: true
  flashings_integrated: true
sealants:
  joints_prepped: true
  tooled: true
  adhesion_fail: false
  weeps_blocked: false
water_test:
  required: true
  performed: true
  passed: true
air_test:
  required: true
  performed: true
  passed: true
drainage:
  requires_protection: true
  protection_installed: true
  drains_clear: true
  standing_water: false
weather:
  temp_f: 62
  wind_kph: 18
  active_precip: false
crew:
  roles:
    - envelope_lead
    - membrane_tech
    - flashing_tech
    - sealant_tech
    - glazier
    - qc_tech
    - safety_watch
  headcount: 9
  briefing_complete: true
  fatigued_workers: []
qa:
  pre_hold_points_clear: true
  install_hold_points_clear: true
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_envelope_go.yaml", go)
    write(studio / "samples" / "pre_envelope_go.yaml", go)
    write(agents_root / "fixtures" / "below_grade_protection_hold.yaml", """zone_id: DEMO-EAST-WALL
substrate:
  clean: true
  dry: true
  cured: true
  voids_patched: true
below_grade:
  membrane_installed: true
  laps_sealed: true
  no_pinholes: true
  wet_film_mils: 65
  protection_board: false
drainage:
  requires_protection: true
  protection_installed: false
  drains_clear: true
weather:
  temp_f: 55
  wind_kph: 10
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "water_test_fail.yaml", """zone_id: DEMO-ROOF-B
water_test:
  required: true
  performed: true
  passed: false
  notes: leakage at curb flashing
roofing:
  primer_ok: true
  laps_ok: true
  seams_accepted: true
curtain_wall:
  setting_blocks_ok: true
  perimeter_sealed: true
  anchorage_ok: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "backfill_abort.yaml", """zone_id: DEMO-EAST-WALL
below_grade:
  membrane_installed: true
  laps_sealed: true
  no_pinholes: true
  protection_board: false
  backfill_without_protection: true
substrate:
  clean: true
  dry: true
  cured: true
drainage:
  requires_protection: true
  protection_installed: false
weather:
  temp_f: 58
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "cold_weather_hold.yaml", """zone_id: DEMO-ROOF-B
substrate:
  clean: true
  dry: true
  cured: true
  slope_ok: true
wrb:
  installed: true
  laps_sealed: true
  transitions_detailed: true
weather:
  temp_f: 32
  membrane_min_f: 40
  wind_kph: 12
crew:
  roles: [envelope_lead, membrane_tech, flashing_tech, sealant_tech, qc_tech, safety_watch]
  briefing_complete: true
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")

    write(ROOT / "tests" / "test_envelope_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.envelope_swarm.swarm import EnvelopeSwarm
from modules.envelope_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "envelope" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(EnvelopeSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_envelope_go():
    assert EnvelopeSwarm().run("pre-envelope-gate", _load("pre_envelope_go.yaml")).decision == "GO"


def test_below_grade_protection_hold():
    r = EnvelopeSwarm().run("below-grade-wp-runbook", _load("below_grade_protection_hold.yaml"))
    assert r.decision == "HOLD"


def test_roofing_go():
    assert EnvelopeSwarm().run("roofing-membrane-runbook", _load("pre_envelope_go.yaml")).decision == "GO"


def test_water_test_fail_hold():
    r = EnvelopeSwarm().run("water-test-gate", _load("water_test_fail.yaml"))
    assert r.decision == "HOLD"
    assert next(g for g in r.gates if g.agent == "water-test").status == "FAIL"


def test_backfill_abort():
    assert EnvelopeSwarm().run("below-grade-wp-runbook", _load("backfill_abort.yaml")).decision == "ABORT"


def test_cold_weather_hold():
    assert EnvelopeSwarm().run("pre-envelope-gate", _load("cold_weather_hold.yaml")).decision == "HOLD"


def test_curtain_wall_go():
    assert EnvelopeSwarm().run("curtain-wall-install-gate", _load("pre_envelope_go.yaml")).decision == "GO"


def test_closeout_go():
    assert EnvelopeSwarm().run("envelope-closeout", _load("pre_envelope_go.yaml")).decision == "GO"


def test_hold_abort():
    assert EnvelopeSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "open edge"}).decision == "ABORT"
''')

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "EnvelopeWaterproofing-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
