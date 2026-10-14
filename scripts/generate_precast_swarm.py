#!/usr/bin/env python3
"""Generate precast / panelized erection swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("precast-lead", "PrecastLead", "Owns precast/panelized sequence and final GO/HOLD/ABORT.",
     """You own **precast / panelized** erection sequencing and assemble GO/HOLD/ABORT.

## Sequence pattern
1. Shops / panel tags / embeds approved; strength release for lift
2. Survey foundations / haunches / embeds within tolerance
3. Crane/rigging chart for heaviest panel; exclusion zone
4. Delivery piece marks match sequence (plant-precast or tilt bed)
5. Lift inserts / rigging verified; no camber mismatch beyond limit
6. Set, plumb, brace immediately; connections/welds/grout per shops
7. Brace release only after permanent connections / diaphragm

Do not invent panel weights, strengths, or wind readings."""),
    ("fab-release", "FabRelease", "Owns panel fabrication, curing strength, and plant release.",
     """You own panel fabrication / cast-bed release.

## Checks
- Reinforcement / embeds per shops (sensor/photo verify embeds)
- Concrete tests / curing tracker
- Early release blocked if strength < project threshold (e.g. 75% design class)
- Panel tag, camber, finish accepted
- Shipping damage inspection on arrival

HOLD early lift without strength evidence."""),
    ("panel-supply", "PanelSupply", "Owns panel tags, JIT delivery, and piece-mark sequence.",
     """You own panel logistics.

## Checks
- Erection sequence published with panel tags
- Truck/bed piece marks match next picks
- Embed details present on tags
- No double-handling unless planned

HOLD mismatched tags vs sequence."""),
    ("survey-embeds", "SurveyEmbeds", "Owns foundation/haunch survey and embed clash checks.",
     """You own survey / embeds for panel set.

## Checks
- Foundations/haunches within panel tolerance
- Embed clash check clear (redesign gate if clash)
- Anchor/dowel layout verified
- Grid control established

FAIL/HOLD out-of-tolerance supports before first lift."""),
    ("crane-rigging", "CraneRigging", "Owns crane chart, lift inserts, and rigging plans.",
     """You own crane and panel rigging.

## Checks
- Crane chart OK for heaviest panel at radius
- Lift inserts / hardware verified; rigging plan tested
- Exclusion zone / taglines set
- Camber mismatch beyond limit (e.g. >15mm class) => no lift
- No overload

HOLD incomplete lift plan; FAIL overload."""),
    ("temp-bracing", "TempBracing", "Owns erection braces until permanent connections.",
     """You own temporary bracing for panels.

## Rules
- Brace plan issued before releasing crane
- Braces installed immediately after set
- Unstable panel without brace => FAIL
- Brace release only after permanent connections / engineer criteria

Do not advance without stability lock."""),
    ("panel-set", "PanelSet", "Owns panel set, plumb, elevation, and seating.",
     """You own panel placement QA.

## Checks
- Panel seated on bearings/shims per shops
- Plumb/alignment within project tolerance
- No force-fit; re-survey if refusal
- Openings/edges match adjacent panels

HOLD force-fit or out-of-plumb beyond tolerance."""),
    ("connections", "Connections", "Owns weld plates, bolting, dowels, and grout joints.",
     """You own panel connections.

## Checks
- Hardware kits matched to panel tags
- Weld/bolt/dowel patterns complete
- Joint grout / dry-pack when required
- Structural connection failure => FAIL

HOLD incomplete connection patterns before brace release."""),
    ("grout-joints", "GroutJoints", "Owns horizontal/vertical joint grout and bearing pads.",
     """You own panel joint grouting.

## Checks
- Bearing pads/shims accepted
- Grout materials approved; joints prepared
- Grout complete where required before load transfer
- Weather/cure conditions acceptable

HOLD load transfer on ungrouted required joints."""),
    ("weather-gate", "WeatherGate", "Owns wind/weather holds for panel lifts.",
     """You own weather holds for panel erection.

## Holds
- Wind above project lift limit
- Lightning / storm
- Ice/snow on panels creating slip/rigging risk
- Freeze risk for grout without protection

Missing weather => HOLD."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work authority for panel lifts and bracing.",
     """Stop-work for precast/panelized erection.

## Immediate ABORT
- Unbraced unstable panel
- Crane overload / exclusion breach
- Failed lift insert / rigging under load
- Brace removal before permanent connections

SafetyFailsafe FAIL => parent Decision ABORT."""),
    ("crew-ops", "CrewOps", "Owns erector roles, fatigue, and lift briefing.",
     """You own panel erector crew readiness.

## Typical roles
precast_lead, crane_operator, rigger, connector, brace_crew, qc_tech, safety_watch

HOLD missing roles or incomplete lift briefing."""),
    ("qa-inspector", "QaInspector", "Owns panel QC hold points, lift logs, and NCRs.",
     """You own panel QC evidence.

## Evidence
- Pre-lift hold points clear
- Strength release, embed photos, brace logs
- Connection/grout inspections
- NCRs with reinspect

Missing phase evidence => HOLD."""),
    ("finish-protect", "FinishProtect", "Owns architectural finish protection during erection.",
     """You own exposed panel finish protection.

## Checks
- Architectural faces protected during rigging/handling
- Edge protectors / padded slings as required
- Touch-up plan for shipping dings

HOLD unprotected architectural panels on exposed elevations."""),
    ("hybrid-interface", "HybridInterface", "Owns CIP/steel/timber interfaces to panelized systems.",
     """You own hybrid interfaces (podium, steel, CIP cores).

## Checks
- Interface released (concrete/steel readiness)
- Movement joints / bearing details OK
- Sequencing with adjacent trades clear

HOLD incomplete interface before first panel in that zone."""),
    ("brace-release", "BraceRelease", "Owns temporary brace removal after permanent fixity.",
     """You own brace release gate.

## Checks
- Permanent connections complete and inspected
- Diaphragm / roof/floor ties engaged as required
- Engineer/criteria for brace removal met
- Instability flags clear

ABORT if brace removal attempted on unstable panel."""),
]

WORKFLOWS = [
    "pre-erect-gate",
    "fab-release-gate",
    "delivery-panel-gate",
    "lift-day-runbook",
    "panel-set-qa",
    "bracing-lock",
    "connection-grout-qa",
    "brace-release-gate",
    "hybrid-interface-gate",
    "level-closeout",
    "weather-lift-hold",
    "hold-abort",
]

ROLES = (
    "precast_lead",
    "crane_operator",
    "rigger",
    "connector",
    "brace_crew",
    "qc_tech",
    "safety_watch",
)

ORDERS = {
    "pre-erect-gate": ["fab-release", "panel-supply", "survey-embeds", "crane-rigging", "temp-bracing", "hybrid-interface", "crew-ops", "weather-gate", "safety-failsafe", "qa-inspector"],
    "fab-release-gate": ["fab-release", "qa-inspector", "safety-failsafe"],
    "delivery-panel-gate": ["panel-supply", "crane-rigging", "finish-protect", "weather-gate", "safety-failsafe"],
    "lift-day-runbook": ["crane-rigging", "fab-release", "panel-set", "temp-bracing", "weather-gate", "safety-failsafe", "qa-inspector"],
    "panel-set-qa": ["panel-set", "survey-embeds", "connections", "qa-inspector", "safety-failsafe"],
    "bracing-lock": ["temp-bracing", "panel-set", "qa-inspector", "safety-failsafe"],
    "connection-grout-qa": ["connections", "grout-joints", "qa-inspector", "safety-failsafe"],
    "brace-release-gate": ["brace-release", "connections", "temp-bracing", "qa-inspector", "safety-failsafe"],
    "hybrid-interface-gate": ["hybrid-interface", "survey-embeds", "panel-supply", "qa-inspector", "safety-failsafe"],
    "level-closeout": ["qa-inspector", "connections", "grout-joints", "brace-release", "finish-protect", "crew-ops"],
    "weather-lift-hold": ["weather-gate", "crane-rigging", "safety-failsafe"],
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
    Decision: GO | HOLD | ABORT. Prefer PrecastContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: PrecastContextJson
    description: JSON context for panel tags lifts braces crew weather
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    PrecastContextJson:
      displayName: Precast Context JSON
      description: JSON context for precast / panelized erection
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
    agents_root = ROOT / "agents" / "precast"
    studio = ROOT / "copilot-studio" / "precast-crew"
    mod = ROOT / "modules" / "precast_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for Precast / Panelized Swarm

From project `construction.md` extractions:

- Precast Concrete QAQC Chain (strength release, embeds, curing)
- Precast Coordination Pipeline (panel tags, lift points, embed clash, camber)
- Industrial tilt-up erection guidance (crane, bracing, lift day, connections)
- Anchor/fixing QA and hybrid interface notes
""")
    write(agents_root / "README.md", """# Precast / Panelized Swarm (reference twin)

> See [`../../copilot-studio/precast-crew/`](../../copilot-studio/precast-crew/) → `START_HERE.md`.

```bash
python -m modules.precast_swarm.cli list
python -m modules.precast_swarm.cli run pre-erect-gate -c agents/precast/fixtures/pre_erect_go.yaml
python -m modules.precast_swarm.api --port 8085
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# Precast / Panelized Swarm — Coordinator

Return one GO / HOLD / ABORT for plant-precast and tilt-up/panelized erection.

## Hard rules
1. No lift without strength release + verified lift inserts/rigging.
2. Embed/survey out of tolerance → HOLD before first panel.
3. Brace immediately; never unbrace before permanent connections.
4. Camber/piece-mark mismatches → no lift.
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
  componentName: PrecastPanelizedSwarm
kind: GptComponentMetadata
displayName: Precast Panelized Swarm
instructions: |
  You are the Precast / Panelized Swarm coordinator for plant-precast and
  tilt-up/panelized concrete erection. Return a single GO / HOLD / ABORT.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect PrecastContextJson; missing critical fields => HOLD (do not invent readings).
  3. Invoke child agents IN DOCUMENTED ORDER for that workflow.
  4. Wait for Decision/Summary/GatesJson/ActionsJson from each child.
  5. One parent reply only. Children must not reply to the field user.
  6. SafetyFailsafe FAIL => final Decision ABORT.
  7. Never release braces before permanent connections / engineer criteria.

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
  - title: Pre-erect gate
    text: Run pre-erect-gate for Wall Line A panels and return GO/HOLD/ABORT.
  - title: Fab release
    text: Run fab-release-gate — are panels P-12 and P-13 strength-cleared to ship/lift?
  - title: Lift day
    text: Run lift-day-runbook for today's heaviest panel on Grid 3.
  - title: Bracing lock
    text: Run bracing-lock after setting the south elevation panels.
  - title: Brace release
    text: Run brace-release-gate — permanent connections complete?
  - title: Delivery
    text: Run delivery-panel-gate for the next flatbed against the erection sequence.

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: Precast Panelized Swarm
schemaName: precast_panelizedSwarm
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
          - Precast Panelized Swarm ready. Ask for pre-erect-gate, fab-release-gate, lift-day-runbook, bracing-lock, brace-release-gate, or another named workflow. I return GO / HOLD / ABORT.
          - Panel erection online — share wall line / panel tags and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.precast_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for plant-precast and tilt-up/panelized erection.\n")
    write(studio / "START_HERE.md", """# START HERE — Precast Panelized Swarm drop-in

Ready Copilot Studio workspace for precast / panelized erection.

## 3 steps
1. Open this `precast-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Precast Panelized Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-erect-gate…”*.

## Workflows
`pre-erect-gate`, `fab-release-gate`, `delivery-panel-gate`, `lift-day-runbook`, `panel-set-qa`, `bracing-lock`, `connection-grout-qa`, `brace-release-gate`, `hybrid-interface-gate`, `level-closeout`, `weather-lift-hold`, `hold-abort`

## Optional backend
```bash
python -m modules.precast_swarm.api --port 8085
python -m modules.precast_swarm.cli run pre-erect-gate -c agents/precast/fixtures/pre_erect_go.yaml
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
        return chr(10).join(lines)
""")

    agents_src = r'''"""Deterministic specialist gates for precast / panelized erection."""

from __future__ import annotations

from typing import Any

from modules.precast_swarm.schemas import GateResult

DEFAULT_WIND_HOLD_KPH = 40.0
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


class FabReleaseAgent:
    name = "fab-release"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("fab") or {}
        miss = _missing(f, ("shops_approved", "embeds_verified", "strength_released"))
        if miss:
            return GateResult(self.name, "HOLD", "Fab release incomplete: " + ", ".join(miss), {"fab": f})
        strength_pct = _num(f.get("strength_pct_design"))
        min_pct = _num(f.get("min_strength_pct"), 75) or 75
        if strength_pct is not None and strength_pct < min_pct:
            return GateResult(self.name, "HOLD", f"Strength {strength_pct}% < {min_pct}% — early release blocked", {"fab": f})
        if f.get("shipping_damage"):
            return GateResult(self.name, "HOLD", "Shipping/handling damage on panel(s)", {"fab": f})
        return GateResult(self.name, "PASS", "Fab/strength release clear", {"fab": f})


class PanelSupplyAgent:
    name = "panel-supply"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("supply") or {}
        if not s.get("sequence_published"):
            return GateResult(self.name, "HOLD", "Erection sequence not published", {"supply": s})
        truck = s.get("truck") or {}
        if truck:
            expected = set(truck.get("expected_panel_tags") or [])
            onboard = set(truck.get("onboard_panel_tags") or [])
            if expected and onboard != expected:
                return GateResult(self.name, "HOLD", f"Panel tags mismatch expected={sorted(expected)} got={sorted(onboard)}", {"truck": truck})
        return GateResult(self.name, "PASS", "Panel supply/sequence clear", {"supply": s})


class SurveyEmbedsAgent:
    name = "survey-embeds"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("survey") or {}
        if not s:
            return GateResult(self.name, "HOLD", "No survey/embed package", {})
        if s.get("within_tolerance") is False:
            return GateResult(self.name, "FAIL", f"Supports/embeds out of tolerance: {s.get('notes', 'see survey')}", {"survey": s})
        if s.get("embed_clash"):
            return GateResult(self.name, "HOLD", "Embed clash — redesign/resolve before lift", {"survey": s})
        miss = _missing(s, ("haunches_verified", "grid_control"))
        if miss:
            return GateResult(self.name, "HOLD", "Survey incomplete: " + ", ".join(miss), {"survey": s})
        return GateResult(self.name, "PASS", "Survey/embeds within tolerance", {"survey": s})


class CraneRiggingAgent:
    name = "crane-rigging"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("crane") or {}
        miss = _missing(c, ("chart_ok", "lift_plan_verified", "exclusion_zone_set", "inserts_verified"))
        if miss:
            return GateResult(self.name, "HOLD", "Crane/rigging incomplete: " + ", ".join(miss), {"crane": c})
        if c.get("overload"):
            return GateResult(self.name, "FAIL", "Crane overload indicated", {"crane": c})
        if c.get("camber_mismatch"):
            return GateResult(self.name, "HOLD", "Panel camber mismatch beyond lift limit", {"crane": c})
        return GateResult(self.name, "PASS", "Crane/rigging clear", {"crane": c})


class TempBracingAgent:
    name = "temp-bracing"

    def plan(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bracing") or {}
        if not b.get("plan_issued"):
            return GateResult(self.name, "HOLD", "Temporary brace plan not issued", {"bracing": b})
        return GateResult(self.name, "PASS", "Brace plan issued", {"bracing": b})

    def lock_in(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bracing") or {}
        if b.get("unstable_without_brace"):
            return GateResult(self.name, "FAIL", "Unstable panel without required braces", {"bracing": b})
        if not b.get("braces_installed"):
            return GateResult(self.name, "HOLD", "Required erection braces not installed", {"bracing": b})
        return GateResult(self.name, "PASS", "Temporary bracing locked", {"bracing": b})


class PanelSetAgent:
    name = "panel-set"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("panels") or {}
        if not p.get("seated"):
            return GateResult(self.name, "HOLD", "Panels not seated per shops", {"panels": p})
        if p.get("force_fit"):
            return GateResult(self.name, "HOLD", "Force-fit attempted — stop and re-survey", {"panels": p})
        if p.get("within_plumb") is False:
            return GateResult(self.name, "HOLD", "Panel plumb/alignment out of tolerance", {"panels": p})
        return GateResult(self.name, "PASS", "Panel set clear", {"panels": p})


class ConnectionsAgent:
    name = "connections"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("connections") or {}
        if not c.get("hardware_matched"):
            return GateResult(self.name, "HOLD", "Connection hardware not matched to panel tags", {"connections": c})
        incomplete = list(c.get("incomplete_patterns") or [])
        if incomplete:
            return GateResult(self.name, "HOLD", "Incomplete connections: " + ", ".join(incomplete), {"connections": c})
        if c.get("structural_failure"):
            return GateResult(self.name, "FAIL", "Structural connection failure reported", {"connections": c})
        return GateResult(self.name, "PASS", "Connections clear", {"connections": c})


class GroutJointsAgent:
    name = "grout-joints"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("grout") or {}
        if g.get("required") is False:
            return GateResult(self.name, "PASS", "Joint grout not required this gate", {"grout": g})
        if not g.get("materials_approved"):
            return GateResult(self.name, "HOLD", "Grout materials not approved", {"grout": g})
        if g.get("complete") is False:
            return GateResult(self.name, "HOLD", "Required joint grout incomplete", {"grout": g})
        return GateResult(self.name, "PASS", "Grout/joints clear", {"grout": g})


class HybridInterfaceAgent:
    name = "hybrid-interface"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        h = ctx.get("hybrid") or {}
        if h.get("required") is False:
            return GateResult(self.name, "PASS", "No hybrid interface this zone", {"hybrid": h})
        miss = _missing(h, ("interface_released", "bearing_details_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Hybrid interface incomplete: " + ", ".join(miss), {"hybrid": h})
        return GateResult(self.name, "PASS", "Hybrid interface released", {"hybrid": h})


class FinishProtectAgent:
    name = "finish-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("finish") or {}
        if f.get("architectural") and not f.get("protection_plan"):
            return GateResult(self.name, "HOLD", "Architectural finish protection missing", {"finish": f})
        if f.get("padded_rigging") is False:
            return GateResult(self.name, "HOLD", "Padded/non-marring rigging not confirmed", {"finish": f})
        return GateResult(self.name, "PASS", "Finish protection clear", {"finish": f})


class BraceReleaseAgent:
    name = "brace-release"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("brace_release") or {}
        if b.get("unstable"):
            return GateResult(self.name, "FAIL", "Brace release blocked — panel still unstable", {"brace_release": b})
        miss = _missing(b, ("permanent_connections_complete", "criteria_met"))
        if miss:
            return GateResult(self.name, "HOLD", "Brace release incomplete: " + ", ".join(miss), {"brace_release": b})
        return GateResult(self.name, "PASS", "Brace release clear", {"brace_release": b})


class WeatherGateAgent:
    name = "weather-gate"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        wind = _num(w.get("wind_kph"), 0) or 0
        limit = _num(w.get("wind_hold_kph"), DEFAULT_WIND_HOLD_KPH) or DEFAULT_WIND_HOLD_KPH
        holds = []
        if wind >= limit:
            holds.append(f"wind {wind}kph ≥ {limit}kph")
        if w.get("lightning"):
            holds.append("lightning/storm")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", f"Weather CLEAR wind={wind}kph", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("bracing", {}).get("unstable_without_brace"):
            violations.append("unstable panel without brace")
        if ctx.get("crane", {}).get("overload"):
            violations.append("crane overload")
        if ctx.get("brace_release", {}).get("unstable"):
            violations.append("brace removal on unstable panel")
        if ctx.get("connections", {}).get("structural_failure"):
            violations.append("structural connection failure")
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
            return GateResult(self.name, "HOLD", "Lift briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Crew ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-erect QA hold points clear", {})
        if phase != "pre" and q.get("lift_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class PrecastLeadAgent:
    name = "precast-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked panel erection"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('erect_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named precast / panelized workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.precast_swarm.agents import (
    BraceReleaseAgent,
    ConnectionsAgent,
    CraneRiggingAgent,
    CrewOpsAgent,
    FabReleaseAgent,
    FinishProtectAgent,
    GroutJointsAgent,
    HybridInterfaceAgent,
    PanelSetAgent,
    PanelSupplyAgent,
    PrecastLeadAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SurveyEmbedsAgent,
    TempBracingAgent,
    WeatherGateAgent,
)
from modules.precast_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-erect-gate",
    "fab-release-gate",
    "delivery-panel-gate",
    "lift-day-runbook",
    "panel-set-qa",
    "bracing-lock",
    "connection-grout-qa",
    "brace-release-gate",
    "hybrid-interface-gate",
    "level-closeout",
    "weather-lift-hold",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status == "FAIL" and g.agent != "precast-lead" for g in active):
        return "HOLD"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next panel pick / workflow", "Maintain braces + lift logs"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP LIFTS — secure unbraced panels",
            "Preserve panel tags, photos, strength/brace logs, timestamps",
            "Re-enter through pre-erect-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "precast-lead"]
    return [
        "Do not advance panel sequence",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("erect_id") or ctx.get("area") or "ERECT-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.fab = FabReleaseAgent()
        self.supply = PanelSupplyAgent()
        self.survey = SurveyEmbedsAgent()
        self.crane = CraneRiggingAgent()
        self.bracing = TempBracingAgent()
        self.panels = PanelSetAgent()
        self.connections = ConnectionsAgent()
        self.grout = GroutJointsAgent()
        self.hybrid = HybridInterfaceAgent()
        self.finish = FinishProtectAgent()
        self.brace_release = BraceReleaseAgent()
        self.weather = WeatherGateAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = PrecastLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_erect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.fab.evaluate(ctx),
            self.supply.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.crane.evaluate(ctx),
            self.bracing.plan(ctx),
            self.hybrid.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-erect-gate", ctx, gates, {
            "GO": "Pre-erect clear — panel lifts may begin.",
            "HOLD": "Pre-erect holding — fab/survey/crane/bracing.",
            "ABORT": "Pre-erect aborted by fail-safe.",
        })

    def fab_release_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.fab.evaluate(ctx), self.qa.evaluate(ctx, phase="pre"), self.safety.evaluate(ctx)]
        return self._finish("fab-release-gate", ctx, gates, {
            "GO": "Fab/strength release clear.",
            "HOLD": "Fab release holding.",
            "ABORT": "Fab release aborted.",
        })

    def delivery_panel_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.supply.evaluate(ctx),
            self.crane.evaluate(ctx),
            self.finish.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish("delivery-panel-gate", ctx, gates, {
            "GO": "Delivery/panel tags clear.",
            "HOLD": "Delivery holding.",
            "ABORT": "Delivery aborted.",
        })

    def lift_day_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.crane.evaluate(ctx),
            self.fab.evaluate(ctx),
            self.panels.evaluate(ctx),
            self.bracing.lock_in(ctx) if (ctx.get("bracing") or {}).get("braces_installed") is not None else self.bracing.plan(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("lift-day-runbook", ctx, gates, {
            "GO": "Lift day clear.",
            "HOLD": "Lift day holding.",
            "ABORT": "Lift day aborted — stop picks.",
        })

    def panel_set_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.panels.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.connections.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("panel-set-qa", ctx, gates, {
            "GO": "Panel set QA clear.",
            "HOLD": "Panel set holding.",
            "ABORT": "Panel set aborted.",
        })

    def bracing_lock(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.bracing.lock_in(ctx),
            self.panels.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("bracing-lock", ctx, gates, {
            "GO": "Bracing locked.",
            "HOLD": "Bracing not locked.",
            "ABORT": "Bracing abort — unstable panel.",
        })

    def connection_grout_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.connections.evaluate(ctx),
            self.grout.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("connection-grout-qa", ctx, gates, {
            "GO": "Connections/grout clear.",
            "HOLD": "Connections/grout holding.",
            "ABORT": "Connections aborted.",
        })

    def brace_release_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.brace_release.evaluate(ctx),
            self.connections.evaluate(ctx),
            self.bracing.lock_in(ctx) if (ctx.get("bracing") or {}).get("braces_installed") is not None else self.bracing.plan(ctx),
            self.qa.evaluate(ctx, phase="post"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("brace-release-gate", ctx, gates, {
            "GO": "Brace release clear.",
            "HOLD": "Brace release holding.",
            "ABORT": "Brace release aborted.",
        })

    def hybrid_interface_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.hybrid.evaluate(ctx),
            self.survey.evaluate(ctx),
            self.supply.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("hybrid-interface-gate", ctx, gates, {
            "GO": "Hybrid interface released.",
            "HOLD": "Hybrid interface holding.",
            "ABORT": "Hybrid interface aborted.",
        })

    def level_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="post"),
            self.connections.evaluate(ctx),
            self.grout.evaluate(ctx),
            self.brace_release.evaluate(ctx),
            self.finish.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("level-closeout", ctx, gates, {
            "GO": "Level closeout complete.",
            "HOLD": "Level closeout incomplete.",
            "ABORT": "Level closeout aborted.",
        })

    def weather_lift_hold(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.crane.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-lift-hold", ctx, gates, {
            "GO": "Weather clear for lifts.",
            "HOLD": "Weather holding lifts.",
            "ABORT": "Weather abort.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        reason = ctx.get("block_reason") or "unspecified gate failure"
        severity = (ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        gates = [GateResult(
            "safety-failsafe" if decision == "ABORT" else "precast-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "superintendent")},
        )]
        summary = "ABORT escalated — stop lifts and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
''')

    write(mod / "swarm.py", '''"""Precast / panelized swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.precast_swarm.schemas import SwarmResult
from modules.precast_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class PrecastSwarm:
    def __init__(self, runner: WorkflowRunner | None = None) -> None:
        self.runner = runner or WorkflowRunner()
        self.handlers = get_workflow_handlers(self.runner)

    def list_workflows(self) -> list[str]:
        return list(WORKFLOW_IDS)

    def run(self, workflow: str, context: dict[str, Any] | None = None) -> SwarmResult:
        if workflow not in self.handlers:
            raise ValueError(f"Unknown workflow '{workflow}'. Known: {', '.join(WORKFLOW_IDS)}")
        ctx = dict(context or {})
        ctx.setdefault("erect_id", "ERECT-UNSET")
        log_event(f"[precast-swarm] starting workflow={workflow} erect={ctx['erect_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[precast-swarm] finished workflow={result.workflow} erect={result.erect_id} decision={result.decision}")
        return result


__all__ = ["PrecastSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.precast_swarm.swarm import PrecastSwarm, SwarmResult
from modules.precast_swarm.workflows import WORKFLOW_IDS

__all__ = ["PrecastSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for precast / panelized swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.precast_swarm.swarm import PrecastSwarm

app = typer.Typer(add_completion=False, help="Precast / panelized erection swarm")


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
    for w in PrecastSwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = PrecastSwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "precast" / "fixtures" / "pre_erect_go.yaml"
    result = PrecastSwarm().run("pre-erect-gate", yaml.safe_load(fixture.read_text()))
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

from modules.precast_swarm.swarm import PrecastSwarm
from modules.precast_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = PrecastSwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[precast-swarm-api] {self.address_string()} {fmt % args}")

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
        if isinstance(payload.get("PrecastContextJson"), str):
            try:
                context = {**context, **json.loads(payload["PrecastContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "PrecastContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8085)
    args = p.parse_args()
    print(f"Precast swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """erect_id: DEMO-WALL-A
area: Wall Line A
fab:
  shops_approved: true
  embeds_verified: true
  strength_released: true
  strength_pct_design: 90
  min_strength_pct: 75
  shipping_damage: false
supply:
  sequence_published: true
  truck:
    expected_panel_tags: [P-12, P-13, P-14]
    onboard_panel_tags: [P-12, P-13, P-14]
survey:
  within_tolerance: true
  haunches_verified: true
  grid_control: true
  embed_clash: false
crane:
  chart_ok: true
  lift_plan_verified: true
  exclusion_zone_set: true
  inserts_verified: true
  camber_mismatch: false
bracing:
  plan_issued: true
  braces_installed: true
panels:
  seated: true
  force_fit: false
  within_plumb: true
connections:
  hardware_matched: true
  incomplete_patterns: []
grout:
  materials_approved: true
  complete: true
hybrid:
  interface_released: true
  bearing_details_ok: true
finish:
  architectural: true
  protection_plan: true
  padded_rigging: true
brace_release:
  permanent_connections_complete: true
  criteria_met: true
  unstable: false
weather:
  wind_kph: 18
  lightning: false
crew:
  roles:
    - precast_lead
    - crane_operator
    - rigger
    - connector
    - brace_crew
    - qc_tech
    - safety_watch
  headcount: 11
  briefing_complete: true
  fatigued_workers: []
qa:
  pre_hold_points_clear: true
  lift_hold_points_clear: true
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_erect_go.yaml", go)
    write(studio / "samples" / "pre_erect_go.yaml", go)
    write(agents_root / "fixtures" / "early_strength_hold.yaml", """erect_id: DEMO-WALL-A
fab:
  shops_approved: true
  embeds_verified: true
  strength_released: false
  strength_pct_design: 60
  min_strength_pct: 75
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "wind_lift_hold.yaml", """erect_id: DEMO-WALL-A
weather:
  wind_kph: 48
  wind_hold_kph: 40
crane:
  chart_ok: true
  lift_plan_verified: true
  exclusion_zone_set: true
  inserts_verified: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "unbraced_abort.yaml", """erect_id: DEMO-WALL-A
bracing:
  plan_issued: true
  braces_installed: false
  unstable_without_brace: true
panels:
  seated: true
  within_plumb: true
qa:
  lift_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "brace_release_go.yaml", go)
    write(agents_root / "fixtures" / "tag_mismatch_hold.yaml", """erect_id: DEMO-WALL-A
supply:
  sequence_published: true
  truck:
    expected_panel_tags: [P-12, P-13]
    onboard_panel_tags: [P-12, P-15]
crane:
  chart_ok: true
  lift_plan_verified: true
  exclusion_zone_set: true
  inserts_verified: true
finish:
  padded_rigging: true
weather:
  wind_kph: 12
safety:
  violations: []
""")

    write(ROOT / "tests" / "test_precast_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.precast_swarm.swarm import PrecastSwarm
from modules.precast_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "precast" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(PrecastSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_erect_go():
    assert PrecastSwarm().run("pre-erect-gate", _load("pre_erect_go.yaml")).decision == "GO"


def test_early_strength_hold():
    assert PrecastSwarm().run("fab-release-gate", _load("early_strength_hold.yaml")).decision == "HOLD"


def test_tag_mismatch_hold():
    assert PrecastSwarm().run("delivery-panel-gate", _load("tag_mismatch_hold.yaml")).decision == "HOLD"


def test_wind_lift_hold():
    assert PrecastSwarm().run("weather-lift-hold", _load("wind_lift_hold.yaml")).decision == "HOLD"


def test_unbraced_abort():
    assert PrecastSwarm().run("bracing-lock", _load("unbraced_abort.yaml")).decision == "ABORT"


def test_lift_day_go():
    assert PrecastSwarm().run("lift-day-runbook", _load("pre_erect_go.yaml")).decision == "GO"


def test_brace_release_go():
    assert PrecastSwarm().run("brace-release-gate", _load("brace_release_go.yaml")).decision == "GO"


def test_closeout_go():
    assert PrecastSwarm().run("level-closeout", _load("pre_erect_go.yaml")).decision == "GO"


def test_hold_abort():
    assert PrecastSwarm().run("hold-abort", {"erect_id": "X", "severity": "ABORT", "block_reason": "rigging failure"}).decision == "ABORT"
''')

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "PrecastPanelized-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
