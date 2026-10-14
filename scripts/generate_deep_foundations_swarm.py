#!/usr/bin/env python3
"""Generate deep foundations field swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("foundations-lead", "FoundationsLead", "Owns deep foundation sequence and final GO/HOLD/ABORT.",
     """You own **deep foundations** (drilled shafts, driven piles, caissons) and assemble GO/HOLD/ABORT.

## Sequence pattern
1. Submittals: mix design, cage shops, pile/shaft schedule, hammer/PDA plan
2. Survey stake-out of pile/shaft centers; utility clear
3. Drill/drive to tip elevation / refusal criteria
4. Clean tip; place cage with cover/spacers
5. Concrete (tremie if wet); document volume vs theoretical
6. Integrity tests (CSL/TIP/PDA) when specified
7. Capacity acceptance / geotech SI sign-off

Do not invent tip elevations, concrete volumes, or test results."""),
    ("materials-concrete", "MaterialsConcrete", "Owns mix design, cage steel, and pile materials.",
     """You own foundation materials readiness.

## Checks
- Concrete mix approved (strength, slump/flow, tremie if wet)
- Cage rebar shops approved; mill certs
- Pile sections / casings certified when driven/cased
- Admixtures / slurry products approved

HOLD missing approvals before first shaft/pile."""),
    ("survey-layout", "SurveyLayout", "Owns stake-out, as-drilled location, and tolerance.",
     """You own foundation layout.

## Checks
- Centers staked from approved plan
- As-drilled/as-driven location within project tolerance
- Cut-off elevation control set

HOLD missing stakes or out-of-tolerance locations before accept."""),
    ("drilling-auger", "DrillingAuger", "Owns drilled-shaft excavation and hole quality.",
     """You own drilled shaft excavation.

## Checks
- Diameter / depth to plan
- Hole verticality within tolerance
- Spoil disposal; no uncontrolled cave-in
- Temporary casing advanced as needed

HOLD hole collapse, wrong diameter, or incomplete depth."""),
    ("casing-slurry", "CasingSlurry", "Owns temporary casing and slurry stability.",
     """You own hole stability methods.

## Checks
- Casing length/seal adequate for soils/water
- Slurry properties (density/viscosity/sand) in spec when used
- No loss of slurry head that risks collapse

HOLD unstable hole or out-of-spec slurry before cage/concrete."""),
    ("tip-elevation", "TipElevation", "Owns tip elevation, cleanout, and bearing stratum.",
     """You own tip acceptance.

## Checks
- Tip at design elevation or approved refusal/bearing criteria
- Cleanout complete (sediment thickness within limit)
- Geotech confirms bearing stratum when required

HOLD high sediment or tip short of criteria."""),
    ("cage-rebar", "CageRebar", "Owns cage assembly, cover, and splice in hole.",
     """You own reinforcing cages.

## Checks
- Cage matches shops; splices/couplers complete
- Centralizers / spacers for cover
- Cage hung at correct elevation; no mud cake contamination on bars if critical

HOLD incomplete cage or missing cover devices before concrete."""),
    ("concrete-placement", "ConcretePlacement", "Owns dry-hole and tremie placement, volume vs theoretical.",
     """You own shaft/pile concrete placement.

## Checks
- Placement method matches hole condition (dry vs tremie)
- Tremie sealed / continuous pour; no cold joints from interruption beyond limit
- Actual volume ≥ theoretical (or documented overbreak reason)
- Slump/flow and tickets logged

HOLD interrupted tremie, short volume, or wrong method."""),
    ("pile-driving", "PileDriving", "Owns driven pile hammer energy, blows, and refusal.",
     """You own driven piles.

## Checks
- Hammer / cushion per approved driving criteria
- Blow count / set within criteria; no damage indicators
- Cut-off and splice procedures followed
- PDA/restrike when specified

HOLD refusal short of tip without eng direction, or damaged pile."""),
    ("integrity-testing", "IntegrityTesting", "Owns CSL, TIP, PIT, PDA integrity evidence.",
     """You own integrity testing.

## Checks
- Required tests scheduled/performed (CSL tubes clear, TIP, PIT, PDA)
- Anomalies dispositioned before cover/cap
- Reports attached to shaft/pile ID

HOLD missing required integrity evidence or open anomalies."""),
    ("capacity-acceptance", "CapacityAcceptance", "Owns capacity criteria and production pile acceptance.",
     """You own capacity acceptance.

## Checks
- Test pile / PDA / load-test criteria met when required
- Production piles accepted vs driving/shaft criteria
- Rejects tagged; replacements planned

HOLD capacity not demonstrated for the element type."""),
    ("weather-protect", "WeatherProtect", "Owns weather holds for drill, pour, and drive.",
     """You own weather holds.

## Holds
- Lightning / high wind for crane/drill/drive
- Freeze risk on concrete without cold-weather procedures
- Flooding of open holes without casing/control

HOLD unsafe weather before critical operations."""),
    ("geotech", "Geotech", "Owns geotech SI tip/cleanout and capacity hold points.",
     """You own geotechnical hold points.

## Checks
- Tip/stratum confirmation when ITP requires SI
- Cleanout acceptance
- Capacity / driving criteria concurrence

HOLD missing geotech/SI at required hold points."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work for open holes, rigging, and utility strikes.",
     """You have stop-work authority. FAIL => swarm **ABORT**.

## Fail conditions
- Unprotected open shaft/pile hole (fall hazard)
- Dig/drill without utility locate or after strike
- Crane/rigging failure indicators ignored
- Cave-in / slurry loss with personnel exposure
- Missing competent person / exclusion zone for drill/drive"""),
    ("crew-ops", "CrewOps", "Owns roles, briefing, and fatigue for foundation crews.",
     """You own crew readiness.

## Roles
foundations_lead, drill_op, crane_op, cage_crew, concrete_tech, qc_tech, safety_watch

HOLD missing roles, incomplete briefing, or fatigue risk."""),
    ("qa-inspector", "QaInspector", "Owns ITP hold points and shaft/pile records.",
     """You own deep foundation QA evidence.

## Checks
- Pre-drill/drive hold points signed
- Shaft/pile logs (tip, volume, blows) complete for phase
- NCRs dispositioned before cap/grade beam

HOLD missing ITP evidence."""),
]

WORKFLOWS = [
    "pre-foundation-gate",
    "layout-stake-gate",
    "drilled-shaft-runbook",
    "tip-elevation-gate",
    "cage-placement-gate",
    "tremie-pour-runbook",
    "driven-pile-runbook",
    "integrity-test-gate",
    "capacity-accept-gate",
    "weather-protect-gate",
    "foundations-closeout",
    "hold-abort",
]

ROLES = (
    "foundations_lead",
    "drill_op",
    "crane_op",
    "cage_crew",
    "concrete_tech",
    "qc_tech",
    "safety_watch",
)

ORDERS = {
    "pre-foundation-gate": ["materials-concrete", "survey-layout", "crew-ops", "weather-protect", "safety-failsafe", "qa-inspector", "geotech"],
    "layout-stake-gate": ["survey-layout", "qa-inspector", "safety-failsafe"],
    "drilled-shaft-runbook": ["survey-layout", "drilling-auger", "casing-slurry", "weather-protect", "safety-failsafe", "qa-inspector"],
    "tip-elevation-gate": ["tip-elevation", "geotech", "casing-slurry", "qa-inspector"],
    "cage-placement-gate": ["cage-rebar", "tip-elevation", "safety-failsafe", "qa-inspector"],
    "tremie-pour-runbook": ["materials-concrete", "cage-rebar", "concrete-placement", "weather-protect", "qa-inspector", "safety-failsafe"],
    "driven-pile-runbook": ["materials-concrete", "survey-layout", "pile-driving", "weather-protect", "safety-failsafe", "qa-inspector", "geotech"],
    "integrity-test-gate": ["integrity-testing", "qa-inspector", "geotech"],
    "capacity-accept-gate": ["capacity-acceptance", "integrity-testing", "geotech", "qa-inspector"],
    "weather-protect-gate": ["weather-protect", "safety-failsafe"],
    "foundations-closeout": ["qa-inspector", "survey-layout", "integrity-testing", "capacity-acceptance", "geotech", "crew-ops"],
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
    Decision: GO | HOLD | ABORT. Prefer FoundationsContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: FoundationsContextJson
    description: JSON context for deep foundations shafts piles tip concrete
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    FoundationsContextJson:
      displayName: Foundations Context JSON
      description: JSON context for deep foundations
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
    agents_root = ROOT / "agents" / "deep-foundations"
    studio = ROOT / "copilot-studio" / "deep-foundations-crew"
    mod = ROOT / "modules" / "deep_foundations_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for Deep Foundations Swarm

From project `construction.md` extractions and typical deep foundation ITP practice:

- QA/QC Field Procedures – Drilled Shafts / Caissons (tip, cleanout, tremie, CSL)
- Driven piles – hammer criteria, PDA, splices, cut-off
- Special inspection hold points for tip elevation and capacity
""")
    write(agents_root / "README.md", """# Deep Foundations Swarm (reference twin)

> See [`../../copilot-studio/deep-foundations-crew/`](../../copilot-studio/deep-foundations-crew/) → `START_HERE.md`.

```bash
python -m modules.deep_foundations_swarm.cli list
python -m modules.deep_foundations_swarm.cli run pre-foundation-gate -c agents/deep-foundations/fixtures/pre_foundation_go.yaml
python -m modules.deep_foundations_swarm.api --port 8089
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# Deep Foundations Swarm — Coordinator

Return one GO / HOLD / ABORT for drilled shafts / driven piles / caissons.

## Hard rules
1. No drill/drive without layout + materials ready.
2. Tip cleanout and elevation before cage/concrete.
3. Tremie continuity / volume evidence for wet shafts.
4. Required integrity/capacity tests before accept.
5. SafetyFailsafe FAIL → ABORT (open holes, utilities, rigging).
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
  componentName: DeepFoundationsSwarm
kind: GptComponentMetadata
displayName: Deep Foundations Swarm
instructions: |
  You are the Deep Foundations Swarm coordinator for drilled shafts, driven piles, and caissons.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect FoundationsContextJson; missing critical fields => HOLD (do not invent readings).
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
  - title: Pre-foundation gate
    text: Run pre-foundation-gate for Shaft S-12 and return GO/HOLD/ABORT.
  - title: Tip elevation
    text: Run tip-elevation-gate — cleanout and bearing stratum confirmed?
  - title: Tremie pour
    text: Run tremie-pour-runbook for wet shaft S-12.
  - title: Driven pile
    text: Run driven-pile-runbook for pile P-40 — set and PDA criteria?
  - title: Integrity test
    text: Run integrity-test-gate for CSL on Shaft S-12.
  - title: Capacity accept
    text: Run capacity-accept-gate before pile cap pour.

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: Deep Foundations Swarm
schemaName: deep_foundations_swarm
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
          - Deep Foundations Swarm ready. Ask for pre-foundation-gate, tip-elevation-gate, tremie-pour-runbook, driven-pile-runbook, integrity-test-gate, or another named workflow. I return GO / HOLD / ABORT.
          - Foundations online — share shaft/pile ID context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.deep_foundations_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for drilled shafts / driven piles QA gates.\n")
    write(studio / "START_HERE.md", """# START HERE — Deep Foundations Swarm drop-in

Ready Copilot Studio workspace for deep foundation field gates.

## 3 steps
1. Open this `deep-foundations-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Deep Foundations Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-foundation-gate…”*.

## Workflows
`pre-foundation-gate`, `layout-stake-gate`, `drilled-shaft-runbook`, `tip-elevation-gate`, `cage-placement-gate`, `tremie-pour-runbook`, `driven-pile-runbook`, `integrity-test-gate`, `capacity-accept-gate`, `weather-protect-gate`, `foundations-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.deep_foundations_swarm.api --port 8089
python -m modules.deep_foundations_swarm.cli run pre-foundation-gate -c agents/deep-foundations/fixtures/pre_foundation_go.yaml
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

    agents_src = r'''"""Deterministic specialist gates for deep foundations."""

from __future__ import annotations

from typing import Any

from modules.deep_foundations_swarm.schemas import GateResult

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


class MaterialsConcreteAgent:
    name = "materials-concrete"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("materials") or {}
        miss = _missing(m, ("mix_approved", "cage_shops_approved", "certs_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Materials incomplete: " + ", ".join(miss), {"materials": m})
        return GateResult(self.name, "PASS", "Mix/cage/pile materials clear", {"materials": m})


class SurveyLayoutAgent:
    name = "survey-layout"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("survey") or {}
        if not s.get("staked"):
            return GateResult(self.name, "HOLD", "Pile/shaft centers not staked", {"survey": s})
        if s.get("location_out_of_tolerance"):
            return GateResult(self.name, "HOLD", "As-built location out of tolerance", {"survey": s})
        return GateResult(self.name, "PASS", "Layout/stake clear", {"survey": s})


class DrillingAugerAgent:
    name = "drilling-auger"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("drilling") or {}
        if d.get("required") is False:
            return GateResult(self.name, "SKIP", "No drilled shaft this gate", {})
        if d.get("collapse"):
            return GateResult(self.name, "HOLD", "Hole collapse / cave-in — stabilize", {"drilling": d})
        if d.get("diameter_ok") is False or d.get("depth_ok") is False:
            return GateResult(self.name, "HOLD", "Diameter/depth not to plan", {"drilling": d})
        if d.get("verticality_ok") is False:
            return GateResult(self.name, "HOLD", "Verticality out of tolerance", {"drilling": d})
        return GateResult(self.name, "PASS", "Drilled shaft excavation clear", {"drilling": d})


class CasingSlurryAgent:
    name = "casing-slurry"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("casing_slurry") or {}
        if c.get("required") is False:
            return GateResult(self.name, "PASS", "Dry hole — casing/slurry not required", {"casing_slurry": c})
        if c.get("unstable"):
            return GateResult(self.name, "HOLD", "Hole unstable — advance casing / restore slurry head", {"casing_slurry": c})
        if c.get("slurry_in_spec") is False:
            return GateResult(self.name, "HOLD", "Slurry properties out of spec", {"casing_slurry": c})
        return GateResult(self.name, "PASS", "Casing/slurry stability clear", {"casing_slurry": c})


class TipElevationAgent:
    name = "tip-elevation"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("tip") or {}
        if not t.get("at_criteria"):
            return GateResult(self.name, "HOLD", "Tip not at design elevation/refusal criteria", {"tip": t})
        sediment = _num(t.get("sediment_in"), 0.0) or 0.0
        max_sed = _num(t.get("max_sediment_in"), 1.0) or 1.0
        if sediment > max_sed:
            return GateResult(self.name, "HOLD", f"Sediment {sediment}in > {max_sed}in max — re-clean", {"tip": t})
        if t.get("cleanout_done") is False:
            return GateResult(self.name, "HOLD", "Cleanout not complete", {"tip": t})
        return GateResult(self.name, "PASS", "Tip elevation/cleanout clear", {"tip": t})


class CageRebarAgent:
    name = "cage-rebar"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("cage") or {}
        miss = _missing(c, ("matches_shops", "spacers_ok", "elevation_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Cage incomplete: " + ", ".join(miss), {"cage": c})
        if c.get("contaminated"):
            return GateResult(self.name, "HOLD", "Cage contaminated — clean/replace before concrete", {"cage": c})
        return GateResult(self.name, "PASS", "Cage placement clear", {"cage": c})


class ConcretePlacementAgent:
    name = "concrete-placement"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("concrete") or {}
        if p.get("required") is False:
            return GateResult(self.name, "SKIP", "No concrete placement this gate", {})
        if p.get("wet_hole") and not p.get("tremie"):
            return GateResult(self.name, "HOLD", "Wet hole requires tremie placement", {"concrete": p})
        if p.get("pour_interrupted"):
            return GateResult(self.name, "HOLD", "Tremie/pour interrupted — cold joint risk", {"concrete": p})
        actual = _num(p.get("volume_cy"))
        theoretical = _num(p.get("theoretical_cy"))
        if actual is not None and theoretical is not None and actual + 1e-6 < theoretical and not p.get("short_volume_approved"):
            return GateResult(self.name, "HOLD", f"Volume {actual}cy < theoretical {theoretical}cy", {"concrete": p})
        if not p.get("tickets_logged"):
            return GateResult(self.name, "HOLD", "Concrete tickets/slump not logged", {"concrete": p})
        return GateResult(self.name, "PASS", "Concrete placement clear", {"concrete": p})


class PileDrivingAgent:
    name = "pile-driving"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("driving") or {}
        if p.get("required") is False:
            return GateResult(self.name, "SKIP", "No driven pile this gate", {})
        if p.get("damaged"):
            return GateResult(self.name, "HOLD", "Pile damage indicators — stop and evaluate", {"driving": p})
        if p.get("refusal_short") and not p.get("eng_direction"):
            return GateResult(self.name, "HOLD", "Refusal short of tip without engineer direction", {"driving": p})
        if p.get("criteria_met") is False:
            return GateResult(self.name, "HOLD", "Driving criteria (blows/set/energy) not met", {"driving": p})
        return GateResult(self.name, "PASS", "Driven pile criteria clear", {"driving": p})


class IntegrityTestingAgent:
    name = "integrity-testing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        i = ctx.get("integrity") or {}
        if i.get("required") is False:
            return GateResult(self.name, "PASS", "Integrity testing not required", {"integrity": i})
        if not i.get("tests_complete"):
            return GateResult(self.name, "HOLD", "Required integrity tests incomplete", {"integrity": i})
        if i.get("open_anomalies"):
            return GateResult(self.name, "HOLD", "Integrity anomalies open: " + ", ".join(i["open_anomalies"]), {"integrity": i})
        return GateResult(self.name, "PASS", "Integrity testing clear", {"integrity": i})


class CapacityAcceptanceAgent:
    name = "capacity-acceptance"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("capacity") or {}
        if c.get("required") is False:
            return GateResult(self.name, "PASS", "Capacity gate not required", {"capacity": c})
        if not c.get("criteria_met"):
            return GateResult(self.name, "HOLD", "Capacity criteria not demonstrated", {"capacity": c})
        if c.get("rejects_open"):
            return GateResult(self.name, "HOLD", "Rejected elements not replaced/dispositioned", {"capacity": c})
        return GateResult(self.name, "PASS", "Capacity acceptance clear", {"capacity": c})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        holds = []
        if w.get("lightning") or w.get("high_wind"):
            holds.append("lightning/high wind — crane/drill/drive hold")
        if w.get("freezing") and not w.get("cold_weather_concrete"):
            holds.append("freeze risk without cold-weather concrete procedures")
        if w.get("flooding_holes") and not w.get("casing_control"):
            holds.append("flooding of open holes without casing/control")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/protection CLEAR", {"weather": w})


class GeotechAgent:
    name = "geotech"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("geotech") or {}
        if g.get("required") is False:
            return GateResult(self.name, "PASS", "Geotech hold not required this gate", {"geotech": g})
        if not g.get("tip_confirmed") and ctx.get("require_tip_si"):
            return GateResult(self.name, "HOLD", "Geotech tip/stratum confirmation missing", {"geotech": g})
        if not g.get("accepted"):
            return GateResult(self.name, "HOLD", "Geotech/SI acceptance missing", {"geotech": g})
        return GateResult(self.name, "PASS", "Geotech hold points clear", {"geotech": g})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("hole", {}).get("unprotected"):
            violations.append("unprotected open shaft/pile hole")
        if ctx.get("utilities", {}).get("dig_without_locate") or ctx.get("utilities", {}).get("utility_strike"):
            violations.append("drill/drive without locate or utility strike")
        if ctx.get("rigging", {}).get("unsafe"):
            violations.append("crane/rigging unsafe")
        if ctx.get("casing_slurry", {}).get("personnel_exposure_collapse"):
            violations.append("cave-in/slurry loss with personnel exposure")
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
            return GateResult(self.name, "PASS", "Pre-foundation QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class FoundationsLeadAgent:
    name = "foundations-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked deep foundation work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('element_id', 'element'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named deep foundation workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.deep_foundations_swarm.agents import (
    CageRebarAgent,
    CapacityAcceptanceAgent,
    CasingSlurryAgent,
    ConcretePlacementAgent,
    CrewOpsAgent,
    DrillingAugerAgent,
    FoundationsLeadAgent,
    GeotechAgent,
    IntegrityTestingAgent,
    MaterialsConcreteAgent,
    PileDrivingAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SurveyLayoutAgent,
    TipElevationAgent,
    WeatherProtectAgent,
)
from modules.deep_foundations_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-foundation-gate",
    "layout-stake-gate",
    "drilled-shaft-runbook",
    "tip-elevation-gate",
    "cage-placement-gate",
    "tremie-pour-runbook",
    "driven-pile-runbook",
    "integrity-test-gate",
    "capacity-accept-gate",
    "weather-protect-gate",
    "foundations-closeout",
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
        return ["Proceed to next foundation sequence / workflow", "Keep shaft/pile logs + integrity records current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — cover/secure open holes; clear exclusion zone",
            "Preserve tip photos, volumes, PDA/CSL data, timestamps",
            "Re-enter through pre-foundation-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "foundations-lead"]
    return [
        "Do not advance cage / concrete / drive / cap pour",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("element_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.materials = MaterialsConcreteAgent()
        self.survey = SurveyLayoutAgent()
        self.drilling = DrillingAugerAgent()
        self.casing = CasingSlurryAgent()
        self.tip = TipElevationAgent()
        self.cage = CageRebarAgent()
        self.concrete = ConcretePlacementAgent()
        self.driving = PileDrivingAgent()
        self.integrity = IntegrityTestingAgent()
        self.capacity = CapacityAcceptanceAgent()
        self.weather = WeatherProtectAgent()
        self.geotech = GeotechAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = FoundationsLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_foundation_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.materials.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
            self.geotech.evaluate(ctx),
        ]
        return self._finish("pre-foundation-gate", ctx, gates, {
            "GO": "Pre-foundation clear — drill/drive sequence may proceed.",
            "HOLD": "Pre-foundation holding — materials/layout/weather.",
            "ABORT": "Pre-foundation aborted by fail-safe.",
        })

    def layout_stake_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.survey.evaluate(ctx), self.qa.evaluate(ctx, phase="pre"), self.safety.evaluate(ctx)]
        return self._finish("layout-stake-gate", ctx, gates, {
            "GO": "Layout/stake clear.",
            "HOLD": "Layout holding.",
            "ABORT": "Layout aborted.",
        })

    def drilled_shaft_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "drilling": {**(ctx.get("drilling") or {}), "required": True}}
        gates = [
            self.survey.evaluate(ctx),
            self.drilling.evaluate(ctx),
            self.casing.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("drilled-shaft-runbook", ctx, gates, {
            "GO": "Drilled shaft excavation clear.",
            "HOLD": "Drilled shaft holding.",
            "ABORT": "Drilled shaft aborted — secure hole.",
        })

    def tip_elevation_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "require_tip_si": True}
        gates = [
            self.tip.evaluate(ctx),
            self.geotech.evaluate(ctx),
            self.casing.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("tip-elevation-gate", ctx, gates, {
            "GO": "Tip elevation/cleanout accepted.",
            "HOLD": "Tip holding — cleanout/stratum.",
            "ABORT": "Tip aborted.",
        })

    def cage_placement_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.cage.evaluate(ctx),
            self.tip.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("cage-placement-gate", ctx, gates, {
            "GO": "Cage placement clear.",
            "HOLD": "Cage holding.",
            "ABORT": "Cage aborted.",
        })

    def tremie_pour_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        conc = {**(ctx.get("concrete") or {}), "required": True, "wet_hole": True, "tremie": (ctx.get("concrete") or {}).get("tremie", True)}
        ctx = {**ctx, "concrete": conc}
        gates = [
            self.materials.evaluate(ctx),
            self.cage.evaluate(ctx),
            self.concrete.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("tremie-pour-runbook", ctx, gates, {
            "GO": "Tremie pour clear.",
            "HOLD": "Tremie pour holding.",
            "ABORT": "Tremie pour aborted.",
        })

    def driven_pile_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "driving": {**(ctx.get("driving") or {}), "required": True}}
        gates = [
            self.materials.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.driving.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.geotech.evaluate(ctx),
        ]
        return self._finish("driven-pile-runbook", ctx, gates, {
            "GO": "Driven pile criteria clear.",
            "HOLD": "Driven pile holding.",
            "ABORT": "Driven pile aborted.",
        })

    def integrity_test_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.integrity.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.geotech.evaluate(ctx),
        ]
        return self._finish("integrity-test-gate", ctx, gates, {
            "GO": "Integrity testing clear.",
            "HOLD": "Integrity testing holding.",
            "ABORT": "Integrity testing aborted.",
        })

    def capacity_accept_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.capacity.evaluate(ctx),
            self.integrity.evaluate(ctx),
            self.geotech.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("capacity-accept-gate", ctx, gates, {
            "GO": "Capacity acceptance clear.",
            "HOLD": "Capacity holding.",
            "ABORT": "Capacity aborted.",
        })

    def weather_protect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-protect-gate", ctx, gates, {
            "GO": "Weather/protection clear.",
            "HOLD": "Weather holding.",
            "ABORT": "Weather aborted.",
        })

    def foundations_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="closeout"),
            self.survey.evaluate(ctx),
            self.integrity.evaluate(ctx),
            self.capacity.evaluate(ctx),
            self.geotech.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("foundations-closeout", ctx, gates, {
            "GO": "Foundations closeout clear.",
            "HOLD": "Foundations closeout holding.",
            "ABORT": "Foundations closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "foundations-lead",
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

    write(mod / "swarm.py", '''"""Deep foundations swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.deep_foundations_swarm.schemas import SwarmResult
from modules.deep_foundations_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class DeepFoundationsSwarm:
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
        log_event(f"[deep-foundations-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[deep-foundations-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["DeepFoundationsSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.deep_foundations_swarm.swarm import DeepFoundationsSwarm, SwarmResult
from modules.deep_foundations_swarm.workflows import WORKFLOW_IDS

__all__ = ["DeepFoundationsSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for deep foundations swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.deep_foundations_swarm.swarm import DeepFoundationsSwarm

app = typer.Typer(add_completion=False, help="Deep foundations field swarm")


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
    for w in DeepFoundationsSwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = DeepFoundationsSwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "deep-foundations" / "fixtures" / "pre_foundation_go.yaml"
    result = DeepFoundationsSwarm().run("pre-foundation-gate", yaml.safe_load(fixture.read_text()))
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

from modules.deep_foundations_swarm.swarm import DeepFoundationsSwarm
from modules.deep_foundations_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = DeepFoundationsSwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[deep-foundations-swarm-api] {self.address_string()} {fmt % args}")

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
        if isinstance(payload.get("FoundationsContextJson"), str):
            try:
                context = {**context, **json.loads(payload["FoundationsContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "FoundationsContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8089)
    args = p.parse_args()
    print(f"Deep foundations swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-SHAFT-S12
element_id: S-12
materials:
  mix_approved: true
  cage_shops_approved: true
  certs_ok: true
survey:
  staked: true
  location_out_of_tolerance: false
drilling:
  required: true
  diameter_ok: true
  depth_ok: true
  verticality_ok: true
  collapse: false
casing_slurry:
  required: true
  unstable: false
  slurry_in_spec: true
tip:
  at_criteria: true
  cleanout_done: true
  sediment_in: 0.25
  max_sediment_in: 1.0
cage:
  matches_shops: true
  spacers_ok: true
  elevation_ok: true
  contaminated: false
concrete:
  required: true
  wet_hole: true
  tremie: true
  pour_interrupted: false
  volume_cy: 42
  theoretical_cy: 40
  tickets_logged: true
driving:
  required: false
integrity:
  required: true
  tests_complete: true
  open_anomalies: []
capacity:
  required: true
  criteria_met: true
  rejects_open: false
weather:
  lightning: false
  high_wind: false
  freezing: false
  cold_weather_concrete: true
  flooding_holes: false
  casing_control: true
geotech:
  tip_confirmed: true
  accepted: true
crew:
  roles:
    - foundations_lead
    - drill_op
    - crane_op
    - cage_crew
    - concrete_tech
    - qc_tech
    - safety_watch
  headcount: 9
  briefing_complete: true
  fatigued_workers: []
qa:
  pre_hold_points_clear: true
  install_hold_points_clear: true
hole:
  unprotected: false
utilities:
  dig_without_locate: false
  utility_strike: false
rigging:
  unsafe: false
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_foundation_go.yaml", go)
    write(studio / "samples" / "pre_foundation_go.yaml", go)
    write(agents_root / "fixtures" / "sediment_hold.yaml", """zone_id: DEMO-SHAFT-S12
tip:
  at_criteria: true
  cleanout_done: true
  sediment_in: 3.0
  max_sediment_in: 1.0
casing_slurry:
  required: true
  unstable: false
  slurry_in_spec: true
geotech:
  tip_confirmed: false
  accepted: false
qa:
  install_hold_points_clear: true
""")
    write(agents_root / "fixtures" / "tremie_interrupt_hold.yaml", """zone_id: DEMO-SHAFT-S12
materials:
  mix_approved: true
  cage_shops_approved: true
  certs_ok: true
cage:
  matches_shops: true
  spacers_ok: true
  elevation_ok: true
concrete:
  wet_hole: true
  tremie: true
  pour_interrupted: true
  volume_cy: 30
  theoretical_cy: 40
  tickets_logged: true
weather:
  lightning: false
  high_wind: false
  freezing: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "open_hole_abort.yaml", """zone_id: DEMO-SHAFT-S12
hole:
  unprotected: true
survey:
  staked: true
drilling:
  required: true
  diameter_ok: true
  depth_ok: true
  verticality_ok: true
casing_slurry:
  required: true
  unstable: false
  slurry_in_spec: true
weather:
  lightning: false
  high_wind: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "driven_refusal_hold.yaml", """zone_id: DEMO-PILE-P40
materials:
  mix_approved: true
  cage_shops_approved: true
  certs_ok: true
survey:
  staked: true
driving:
  required: true
  criteria_met: false
  refusal_short: true
  eng_direction: false
  damaged: false
weather:
  lightning: false
  high_wind: false
geotech:
  accepted: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "integrity_anomaly_hold.yaml", """zone_id: DEMO-SHAFT-S12
integrity:
  required: true
  tests_complete: true
  open_anomalies: [CSL_tube_2_soft_zone]
capacity:
  required: true
  criteria_met: false
  rejects_open: true
geotech:
  accepted: false
qa:
  install_hold_points_clear: true
""")

    write(ROOT / "tests" / "test_deep_foundations_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.deep_foundations_swarm.swarm import DeepFoundationsSwarm
from modules.deep_foundations_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "deep-foundations" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(DeepFoundationsSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_foundation_go():
    assert DeepFoundationsSwarm().run("pre-foundation-gate", _load("pre_foundation_go.yaml")).decision == "GO"


def test_sediment_hold():
    assert DeepFoundationsSwarm().run("tip-elevation-gate", _load("sediment_hold.yaml")).decision == "HOLD"


def test_tremie_interrupt_hold():
    assert DeepFoundationsSwarm().run("tremie-pour-runbook", _load("tremie_interrupt_hold.yaml")).decision == "HOLD"


def test_open_hole_abort():
    assert DeepFoundationsSwarm().run("drilled-shaft-runbook", _load("open_hole_abort.yaml")).decision == "ABORT"


def test_driven_refusal_hold():
    assert DeepFoundationsSwarm().run("driven-pile-runbook", _load("driven_refusal_hold.yaml")).decision == "HOLD"


def test_integrity_anomaly_hold():
    assert DeepFoundationsSwarm().run("capacity-accept-gate", _load("integrity_anomaly_hold.yaml")).decision == "HOLD"


def test_tremie_go():
    assert DeepFoundationsSwarm().run("tremie-pour-runbook", _load("pre_foundation_go.yaml")).decision == "GO"


def test_closeout_go():
    assert DeepFoundationsSwarm().run("foundations-closeout", _load("pre_foundation_go.yaml")).decision == "GO"


def test_hold_abort():
    assert DeepFoundationsSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "open hole"}).decision == "ABORT"
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

### Deep Foundations Swarm (Copilot Studio)

Same pattern — field GO/HOLD/ABORT for drilled shafts, driven piles, and caissons:

- [`copilot-studio/deep-foundations-crew/`](copilot-studio/deep-foundations-crew/) — parent + 16 child agents; open `START_HERE.md`
- Drop-in zip: [`packages/DeepFoundations-Swarm-CopilotStudio-DropIn.zip`](packages/DeepFoundations-Swarm-CopilotStudio-DropIn.zip)

```bash
python -m modules.deep_foundations_swarm.api --port 8089
python -m modules.deep_foundations_swarm.cli run pre-foundation-gate -c agents/deep-foundations/fixtures/pre_foundation_go.yaml
```
"""
        if "Deep Foundations Swarm" not in rtxt and marker in rtxt:
            readme.write_text(rtxt.replace(marker, block + "\n", 1))

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "DeepFoundations-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
