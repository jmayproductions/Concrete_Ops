#!/usr/bin/env python3
"""Generate heavy-lift / crane day field swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("lift-lead", "LiftLead", "Owns heavy-lift sequence and final GO/HOLD/ABORT.",
     """You own **heavy-lift / crane day** sequencing and assemble GO/HOLD/ABORT.

## Sequence pattern
1. Lift plan + load chart + certifications approved
2. Ground bearing / mats / outriggers set
3. Rigging inspected; pick path and exclusion clear
4. Power line clearances; wind/weather within limits
5. Signal/comms confirmed; critical/tandem extras when required
6. Post-lift secure and closeout

Do not invent load weights, radii, or wind speeds."""),
    ("lift-plan", "LiftPlan", "Owns written lift plan and critical-lift classification.",
     """You own the lift plan.

## Checks
- Written plan for critical/complex lifts
- Load weight, CG, radius, crane config documented
- Roles (operator, rigger, signal) named

HOLD starting critical lift without approved plan."""),
    ("crane-certs", "CraneCerts", "Owns crane, operator, and rigger qualifications.",
     """You own certifications.

## Checks
- Crane annual/periodic inspection current
- Operator certified for crane type
- Qualified rigger / signal person as required

HOLD lift with expired certs or unqualified crew."""),
    ("ground-bearing", "GroundBearing", "Owns crane setup, mats, and ground bearing pressure.",
     """You own crane support/setup.

## Checks
- Outriggers fully extended / set per chart
- Mats/cribbing sized for bearing pressure
- Soft/void ground identified and remediated

HOLD setup on unverified soft ground or incomplete outriggers."""),
    ("rigging-gear", "RiggingGear", "Owns sling/shackle inspection and capacity.",
     """You own rigging gear.

## Checks
- Slings/shackles/hardware inspected; tags readable
- Capacity ≥ load with required D/d and angles
- Damaged gear removed from service

HOLD/FAIL use of damaged or undersized rigging."""),
    ("pick-path", "PickPath", "Owns swing path, travel, and obstruction clearance.",
     """You own pick path.

## Checks
- Swing/travel path clear of structures and workers
- Tag lines planned; no blind picks without controls
- Laydown / set point prepared

HOLD obstructed or uncontrolled pick path."""),
    ("power-lines", "PowerLines", "Owns power line clearances and spotters.",
     """You own power line hazard control.

## Checks
- Distances meet OSHA/table requirements or dedicated spotter/plan
- Encroachment alarms / dedicated spotter when required
- De-energize/insulate when plan requires

FAIL boom/load in prohibited proximity without controls."""),
    ("exclusion-zone", "ExclusionZone", "Owns lift exclusion zone and access control.",
     """You own exclusion zones.

## Checks
- Zone marked and enforced
- No personnel under load
- Spotters at access points when required

FAIL personnel under suspended load or breached zone."""),
    ("signal-comms", "SignalComms", "Owns signal person and radio protocol.",
     """You own lift communications.

## Checks
- Designated signal person visible/radio to operator
- Standard signals / channel confirmed
- Stop signal authority clear to all

HOLD critical lift with lost/unclear comms."""),
    ("weather-wind", "WeatherWind", "Owns wind, lightning, and visibility holds.",
     """You own weather holds for lifting.

## Holds
- Wind above crane/manufacturer or site limit
- Lightning / severe storm
- Visibility too poor for safe signaling

HOLD or ABORT per severity."""),
    ("load-chart", "LoadChart", "Owns capacity vs radius/config verification.",
     """You own load chart compliance.

## Checks
- Gross load (including rigging) ≤ chart capacity at radius
- Crane config matches chart (boom, counterweight, jib)
- Unknown weight => HOLD until verified

FAIL intentional overload / unknown critical weight."""),
    ("tagline-control", "TagLineControl", "Owns tag lines and load control during swing.",
     """You own tag-line control.

## Checks
- Tag lines used to control spin when required
- Tag-line hands clear of pinch/crush
- No riding the load

HOLD uncontrolled spinning loads in congested areas."""),
    ("tandem-critical", "TandemCritical", "Owns tandem and critical-lift extras.",
     """You own tandem / critical lift extras.

## Checks
- Dual-crane share of load calculated
- Single signal authority; synchronized plan
- Engineering/critical-lift checklist signed when required

HOLD tandem/critical lift without extras complete."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work for under-load, power lines, overload, wind.",
     """You have stop-work authority. FAIL => swarm **ABORT**.

## Fail conditions
- Personnel under suspended load
- Power line encroachment without controls
- Lift in winds above limit / lightning
- Overload or unknown weight on critical pick
- Damaged rigging in use
- Lost comms during critical lift with load on hook"""),
    ("crew-ops", "CrewOps", "Owns lift crew roles and briefing.",
     """You own lift crew readiness.

## Roles
lift_lead, crane_op, rigger, signal_person, spotter, qc_tech, safety_watch

HOLD missing roles or incomplete lift briefing."""),
    ("qa-inspector", "QaInspector", "Owns lift documentation and checklists.",
     """You own lift QA evidence.

## Checks
- Lift plan / chart sheet on file
- Pre-use inspection logged
- Critical-lift checklist signed when required

HOLD missing lift documentation."""),
]

WORKFLOWS = [
    "pre-lift-gate",
    "lift-plan-review",
    "ground-bearing-gate",
    "rigging-inspection",
    "load-chart-gate",
    "power-line-clearance",
    "exclusion-zone-gate",
    "critical-lift-runbook",
    "tandem-lift-gate",
    "weather-wind-gate",
    "post-lift-closeout",
    "hold-abort",
]

ROLES = (
    "lift_lead",
    "crane_op",
    "rigger",
    "signal_person",
    "spotter",
    "qc_tech",
    "safety_watch",
)

ORDERS = {
    "pre-lift-gate": ["lift-plan", "crane-certs", "load-chart", "crew-ops", "weather-wind", "safety-failsafe", "qa-inspector"],
    "lift-plan-review": ["lift-plan", "load-chart", "tandem-critical", "qa-inspector"],
    "ground-bearing-gate": ["ground-bearing", "crane-certs", "qa-inspector", "safety-failsafe"],
    "rigging-inspection": ["rigging-gear", "load-chart", "qa-inspector", "safety-failsafe"],
    "load-chart-gate": ["load-chart", "lift-plan", "qa-inspector", "safety-failsafe"],
    "power-line-clearance": ["power-lines", "pick-path", "safety-failsafe", "qa-inspector"],
    "exclusion-zone-gate": ["exclusion-zone", "signal-comms", "tagline-control", "safety-failsafe", "qa-inspector"],
    "critical-lift-runbook": ["lift-plan", "load-chart", "ground-bearing", "rigging-gear", "power-lines", "exclusion-zone", "signal-comms", "weather-wind", "safety-failsafe", "qa-inspector"],
    "tandem-lift-gate": ["tandem-critical", "lift-plan", "signal-comms", "load-chart", "safety-failsafe", "qa-inspector"],
    "weather-wind-gate": ["weather-wind", "safety-failsafe"],
    "post-lift-closeout": ["qa-inspector", "rigging-gear", "exclusion-zone", "crew-ops"],
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
    Decision: GO | HOLD | ABORT. Prefer LiftContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: LiftContextJson
    description: JSON context for crane lift plan load chart wind exclusion
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    LiftContextJson:
      displayName: Lift Context JSON
      description: JSON context for heavy-lift / crane day
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
    agents_root = ROOT / "agents" / "heavy-lift"
    studio = ROOT / "copilot-studio" / "heavy-lift-crew"
    mod = ROOT / "modules" / "heavy_lift_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for Heavy-Lift / Crane Day Swarm

From project `construction.md` extractions and typical crane ITP practice:

- Lift plan, load chart, and critical/tandem lift controls
- Ground bearing, rigging inspection, power line clearance
- Exclusion zones, signal/comms, and wind/weather holds
""")
    write(agents_root / "README.md", """# Heavy-Lift / Crane Day Swarm (reference twin)

> See [`../../copilot-studio/heavy-lift-crew/`](../../copilot-studio/heavy-lift-crew/) → `START_HERE.md`.

```bash
python -m modules.heavy_lift_swarm.cli list
python -m modules.heavy_lift_swarm.cli run pre-lift-gate -c agents/heavy-lift/fixtures/pre_lift_go.yaml
python -m modules.heavy_lift_swarm.api --port 8096
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# Heavy-Lift Swarm — Coordinator

Return one GO / HOLD / ABORT for crane / heavy-lift operations.

## Hard rules
1. No critical lift without plan + chart + certs.
2. Never lift over people; enforce exclusion.
3. Power line and wind limits are hard stops.
4. Unknown weight or damaged rigging => no lift.
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
  componentName: HeavyLiftCraneSwarm
kind: GptComponentMetadata
displayName: Heavy Lift Crane Swarm
instructions: |
  You are the Heavy-Lift / Crane Day Swarm coordinator.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect LiftContextJson; missing critical fields => HOLD (do not invent readings).
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
  - title: Pre-lift gate
    text: Run pre-lift-gate for Panel P-12 pick and return GO/HOLD/ABORT.
  - title: Critical lift
    text: Run critical-lift-runbook for the rooftop unit.
  - title: Ground bearing
    text: Run ground-bearing-gate — mats and outriggers OK?
  - title: Power lines
    text: Run power-line-clearance for east lot crane.
  - title: Wind hold
    text: Run weather-wind-gate — gusts at 28 mph.
  - title: Tandem lift
    text: Run tandem-lift-gate for dual-crane bridge girder.

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: Heavy Lift Crane Swarm
schemaName: heavy_lift_crane_swarm
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
          - Heavy Lift Crane Swarm ready. Ask for pre-lift-gate, critical-lift-runbook, ground-bearing-gate, power-line-clearance, weather-wind-gate, or another named workflow. I return GO / HOLD / ABORT.
          - Crane day online — share pick/crane context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.heavy_lift_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for heavy-lift / crane day QA gates.\n")
    write(studio / "START_HERE.md", """# START HERE — Heavy Lift Crane Swarm drop-in

Ready Copilot Studio workspace for heavy-lift / crane day field gates.

## 3 steps
1. Open this `heavy-lift-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Heavy Lift Crane Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-lift-gate…”*.

## Workflows
`pre-lift-gate`, `lift-plan-review`, `ground-bearing-gate`, `rigging-inspection`, `load-chart-gate`, `power-line-clearance`, `exclusion-zone-gate`, `critical-lift-runbook`, `tandem-lift-gate`, `weather-wind-gate`, `post-lift-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.heavy_lift_swarm.api --port 8096
python -m modules.heavy_lift_swarm.cli run pre-lift-gate -c agents/heavy-lift/fixtures/pre_lift_go.yaml
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

    agents_src = r'''"""Deterministic specialist gates for heavy-lift / crane day."""

from __future__ import annotations

from typing import Any

from modules.heavy_lift_swarm.schemas import GateResult

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


class LiftPlanAgent:
    name = "lift-plan"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("plan") or {}
        if p.get("critical") and not p.get("approved"):
            return GateResult(self.name, "HOLD", "Critical lift plan not approved", {"plan": p})
        miss = _missing(p, ("weight_known", "radius_known", "roles_named"))
        if miss:
            return GateResult(self.name, "HOLD", "Lift plan incomplete: " + ", ".join(miss), {"plan": p})
        return GateResult(self.name, "PASS", "Lift plan clear", {"plan": p})


class CraneCertsAgent:
    name = "crane-certs"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("certs") or {}
        if c.get("crane_inspection_current") is False:
            return GateResult(self.name, "HOLD", "Crane inspection not current", {"certs": c})
        if c.get("operator_certified") is False:
            return GateResult(self.name, "HOLD", "Operator not certified for crane type", {"certs": c})
        if c.get("rigger_qualified") is False:
            return GateResult(self.name, "HOLD", "Rigger/signal not qualified", {"certs": c})
        return GateResult(self.name, "PASS", "Crane/crew certs clear", {"certs": c})


class GroundBearingAgent:
    name = "ground-bearing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("ground") or {}
        if g.get("outriggers_set") is False:
            return GateResult(self.name, "HOLD", "Outriggers not fully set per chart", {"ground": g})
        if g.get("mats_ok") is False:
            return GateResult(self.name, "HOLD", "Mats/cribbing inadequate for bearing", {"ground": g})
        if g.get("soft_ground"):
            return GateResult(self.name, "HOLD", "Soft/void ground unresolved", {"ground": g})
        return GateResult(self.name, "PASS", "Ground bearing/setup clear", {"ground": g})


class RiggingGearAgent:
    name = "rigging-gear"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        r = ctx.get("rigging") or {}
        if r.get("damaged"):
            return GateResult(self.name, "FAIL", "Damaged rigging in service", {"rigging": r})
        if r.get("capacity_ok") is False:
            return GateResult(self.name, "HOLD", "Rigging capacity/angle insufficient", {"rigging": r})
        if not r.get("inspected"):
            return GateResult(self.name, "HOLD", "Rigging not inspected this shift", {"rigging": r})
        return GateResult(self.name, "PASS", "Rigging gear clear", {"rigging": r})


class PickPathAgent:
    name = "pick-path"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("path") or {}
        if p.get("obstructed"):
            return GateResult(self.name, "HOLD", "Pick/swing path obstructed", {"path": p})
        if p.get("blind_uncontrolled"):
            return GateResult(self.name, "HOLD", "Blind pick without controls", {"path": p})
        return GateResult(self.name, "PASS", "Pick path clear", {"path": p})


class PowerLinesAgent:
    name = "power-lines"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("power_lines") or {}
        if p.get("encroachment"):
            return GateResult(self.name, "FAIL", "Power line encroachment without controls", {"power_lines": p})
        if p.get("present") and not p.get("clearance_ok") and not p.get("spotter_plan"):
            return GateResult(self.name, "HOLD", "Power line clearance/spotter plan incomplete", {"power_lines": p})
        return GateResult(self.name, "PASS", "Power line clearance clear", {"power_lines": p})


class ExclusionZoneAgent:
    name = "exclusion-zone"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("exclusion") or {}
        if e.get("under_load"):
            return GateResult(self.name, "FAIL", "Personnel under suspended load", {"exclusion": e})
        if e.get("breached"):
            return GateResult(self.name, "FAIL", "Exclusion zone breached", {"exclusion": e})
        if not e.get("marked"):
            return GateResult(self.name, "HOLD", "Exclusion zone not marked/enforced", {"exclusion": e})
        return GateResult(self.name, "PASS", "Exclusion zone clear", {"exclusion": e})


class SignalCommsAgent:
    name = "signal-comms"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("comms") or {}
        if s.get("lost_during_critical"):
            return GateResult(self.name, "FAIL", "Lost comms during critical lift", {"comms": s})
        if not s.get("signal_person") or not s.get("channel_confirmed"):
            return GateResult(self.name, "HOLD", "Signal person/comms not confirmed", {"comms": s})
        return GateResult(self.name, "PASS", "Signal/comms clear", {"comms": s})


class WeatherWindAgent:
    name = "weather-wind"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather/wind data", {})
        wind = _num(w.get("wind_mph"))
        limit = _num(w.get("wind_limit_mph"), 20.0) or 20.0
        if w.get("lightning"):
            return GateResult(self.name, "FAIL", "Lightning — stop lifting", {"weather": w})
        if wind is not None and wind > limit:
            return GateResult(self.name, "FAIL", f"Wind {wind} mph > limit {limit} mph", {"weather": w})
        if w.get("poor_visibility"):
            return GateResult(self.name, "HOLD", "Visibility too poor for signaling", {"weather": w})
        return GateResult(self.name, "PASS", "Weather/wind CLEAR", {"weather": w})


class LoadChartAgent:
    name = "load-chart"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("chart") or {}
        if l.get("unknown_weight") and l.get("critical"):
            return GateResult(self.name, "FAIL", "Unknown weight on critical lift", {"chart": l})
        if l.get("unknown_weight"):
            return GateResult(self.name, "HOLD", "Load weight unknown — verify before lift", {"chart": l})
        if l.get("within_chart") is False:
            return GateResult(self.name, "FAIL", "Load exceeds chart capacity at radius/config", {"chart": l})
        if l.get("config_match") is False:
            return GateResult(self.name, "HOLD", "Crane config does not match chart", {"chart": l})
        return GateResult(self.name, "PASS", "Load chart clear", {"chart": l})


class TagLineControlAgent:
    name = "tagline-control"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("taglines") or {}
        if t.get("required") is False:
            return GateResult(self.name, "SKIP", "Tag lines not required", {})
        if t.get("uncontrolled_spin"):
            return GateResult(self.name, "HOLD", "Uncontrolled load spin in congested area", {"taglines": t})
        if t.get("riding_load"):
            return GateResult(self.name, "FAIL", "Personnel riding the load", {"taglines": t})
        return GateResult(self.name, "PASS", "Tag-line control clear", {"taglines": t})


class TandemCriticalAgent:
    name = "tandem-critical"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("tandem") or {}
        if t.get("required") is False:
            return GateResult(self.name, "SKIP", "No tandem/critical extras", {})
        if not t.get("share_calculated"):
            return GateResult(self.name, "HOLD", "Tandem load share not calculated", {"tandem": t})
        if not t.get("single_signal"):
            return GateResult(self.name, "HOLD", "Single signal authority not established", {"tandem": t})
        if t.get("checklist_signed") is False:
            return GateResult(self.name, "HOLD", "Critical/tandem checklist not signed", {"tandem": t})
        return GateResult(self.name, "PASS", "Tandem/critical extras clear", {"tandem": t})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("exclusion") or {}).get("under_load") or (ctx.get("exclusion") or {}).get("breached"):
            violations.append("personnel under load / exclusion breached")
        if (ctx.get("power_lines") or {}).get("encroachment"):
            violations.append("power line encroachment")
        w = ctx.get("weather") or {}
        wind = _num(w.get("wind_mph"))
        limit = _num(w.get("wind_limit_mph"), 20.0) or 20.0
        if w.get("lightning") or (wind is not None and wind > limit):
            violations.append("wind/lightning lift limit exceeded")
        ch = ctx.get("chart") or {}
        if ch.get("within_chart") is False or (ch.get("unknown_weight") and ch.get("critical")):
            violations.append("overload or unknown critical weight")
        if (ctx.get("rigging") or {}).get("damaged"):
            violations.append("damaged rigging in use")
        if (ctx.get("comms") or {}).get("lost_during_critical"):
            violations.append("lost comms during critical lift")
        if (ctx.get("taglines") or {}).get("riding_load"):
            violations.append("riding the load")
        if violations:
            return GateResult(self.name, "FAIL", "STOP-WORK: " + "; ".join(dict.fromkeys(violations)), {"violations": list(dict.fromkeys(violations))})
        return GateResult(self.name, "PASS", "No fail-safe violations", {})


class CrewOpsAgent:
    name = "crew-ops"

    def evaluate(self, ctx: dict[str, Any], require_briefing: bool = True) -> GateResult:
        crew = ctx.get("crew") or {}
        roles = set(crew.get("roles") or [])
        missing = [r for r in ERECT_ROLES if r not in roles]
        if missing:
            return GateResult(self.name, "HOLD", "Missing roles: " + ", ".join(missing), {"missing": missing})
        if require_briefing and not crew.get("briefing_complete"):
            return GateResult(self.name, "HOLD", "Lift briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Lift crew ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-lift docs clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} lift docs clear", {})
        return GateResult(self.name, "HOLD", f"No lift QA evidence for phase={phase}", {"qa": q})


class LiftLeadAgent:
    name = "lift-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked lift"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Lift sequence ready for {ctx.get('zone_id', ctx.get('pick_id', 'pick'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named heavy-lift / crane workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.heavy_lift_swarm.agents import (
    CraneCertsAgent,
    CrewOpsAgent,
    ExclusionZoneAgent,
    GroundBearingAgent,
    LiftLeadAgent,
    LiftPlanAgent,
    LoadChartAgent,
    PickPathAgent,
    PowerLinesAgent,
    QaInspectorAgent,
    RiggingGearAgent,
    SafetyFailsafeAgent,
    SignalCommsAgent,
    TagLineControlAgent,
    TandemCriticalAgent,
    WeatherWindAgent,
)
from modules.heavy_lift_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-lift-gate",
    "lift-plan-review",
    "ground-bearing-gate",
    "rigging-inspection",
    "load-chart-gate",
    "power-line-clearance",
    "exclusion-zone-gate",
    "critical-lift-runbook",
    "tandem-lift-gate",
    "weather-wind-gate",
    "post-lift-closeout",
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
        return ["Proceed with lift under plan controls", "Keep exclusion enforced; re-check wind before pick"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP LIFT — lower/land load if safe; clear exclusion; secure crane",
            "Preserve lift plan, chart sheet, photos, wind log, timestamps",
            "Re-enter through pre-lift-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "lift-lead"]
    return [
        "Do not hoist until cleared",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("pick_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.plan = LiftPlanAgent()
        self.certs = CraneCertsAgent()
        self.ground = GroundBearingAgent()
        self.rigging = RiggingGearAgent()
        self.path = PickPathAgent()
        self.power = PowerLinesAgent()
        self.exclusion = ExclusionZoneAgent()
        self.comms = SignalCommsAgent()
        self.weather = WeatherWindAgent()
        self.chart = LoadChartAgent()
        self.taglines = TagLineControlAgent()
        self.tandem = TandemCriticalAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = LiftLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_lift_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.plan.evaluate(ctx),
            self.certs.evaluate(ctx),
            self.chart.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-lift-gate", ctx, gates, {
            "GO": "Pre-lift clear — setup/pick sequence may proceed.",
            "HOLD": "Pre-lift holding — plan/certs/chart/weather.",
            "ABORT": "Pre-lift aborted by fail-safe.",
        })

    def lift_plan_review(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.plan.evaluate(ctx),
            self.chart.evaluate(ctx),
            self.tandem.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("lift-plan-review", ctx, gates, {
            "GO": "Lift plan review clear.",
            "HOLD": "Lift plan review holding.",
            "ABORT": "Lift plan review aborted.",
        })

    def ground_bearing_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.ground.evaluate(ctx),
            self.certs.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("ground-bearing-gate", ctx, gates, {
            "GO": "Ground bearing/setup clear.",
            "HOLD": "Ground bearing holding.",
            "ABORT": "Ground bearing aborted.",
        })

    def rigging_inspection(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.rigging.evaluate(ctx),
            self.chart.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("rigging-inspection", ctx, gates, {
            "GO": "Rigging inspection clear.",
            "HOLD": "Rigging holding.",
            "ABORT": "Rigging aborted — remove damaged gear.",
        })

    def load_chart_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.chart.evaluate(ctx),
            self.plan.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("load-chart-gate", ctx, gates, {
            "GO": "Load chart clear.",
            "HOLD": "Load chart holding.",
            "ABORT": "Load chart aborted — do not hoist.",
        })

    def power_line_clearance(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.power.evaluate(ctx),
            self.path.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("power-line-clearance", ctx, gates, {
            "GO": "Power line clearance clear.",
            "HOLD": "Power line clearance holding.",
            "ABORT": "Power line aborted — stop boom movement.",
        })

    def exclusion_zone_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.exclusion.evaluate(ctx),
            self.comms.evaluate(ctx),
            self.taglines.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("exclusion-zone-gate", ctx, gates, {
            "GO": "Exclusion/comms clear.",
            "HOLD": "Exclusion/comms holding.",
            "ABORT": "Exclusion aborted — clear people from zone.",
        })

    def critical_lift_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        plan = {**(ctx.get("plan") or {}), "critical": True, "approved": (ctx.get("plan") or {}).get("approved", True)}
        chart = {**(ctx.get("chart") or {}), "critical": True}
        ctx = {**ctx, "plan": plan, "chart": chart}
        gates = [
            self.plan.evaluate(ctx),
            self.chart.evaluate(ctx),
            self.ground.evaluate(ctx),
            self.rigging.evaluate(ctx),
            self.power.evaluate(ctx),
            self.exclusion.evaluate(ctx),
            self.comms.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("critical-lift-runbook", ctx, gates, {
            "GO": "Critical lift runbook clear.",
            "HOLD": "Critical lift holding.",
            "ABORT": "Critical lift aborted.",
        })

    def tandem_lift_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "tandem": {**(ctx.get("tandem") or {}), "required": True}, "plan": {**(ctx.get("plan") or {}), "critical": True}}
        gates = [
            self.tandem.evaluate(ctx),
            self.plan.evaluate(ctx),
            self.comms.evaluate(ctx),
            self.chart.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("tandem-lift-gate", ctx, gates, {
            "GO": "Tandem lift clear.",
            "HOLD": "Tandem lift holding.",
            "ABORT": "Tandem lift aborted.",
        })

    def weather_wind_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-wind-gate", ctx, gates, {
            "GO": "Weather/wind clear for lifting.",
            "HOLD": "Weather holding.",
            "ABORT": "Weather aborted — do not lift.",
        })

    def post_lift_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="closeout"),
            self.rigging.evaluate(ctx),
            self.exclusion.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("post-lift-closeout", ctx, gates, {
            "GO": "Post-lift closeout clear.",
            "HOLD": "Post-lift closeout holding.",
            "ABORT": "Post-lift closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "lift-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "lift_director")},
        )]
        summary = "ABORT escalated — stop lift and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
''')

    write(mod / "swarm.py", '''"""Heavy-lift / crane swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.heavy_lift_swarm.schemas import SwarmResult
from modules.heavy_lift_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class HeavyLiftSwarm:
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
        log_event(f"[heavy-lift-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[heavy-lift-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["HeavyLiftSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.heavy_lift_swarm.swarm import HeavyLiftSwarm, SwarmResult
from modules.heavy_lift_swarm.workflows import WORKFLOW_IDS

__all__ = ["HeavyLiftSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for heavy-lift / crane swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.heavy_lift_swarm.swarm import HeavyLiftSwarm

app = typer.Typer(add_completion=False, help="Heavy-lift / crane day field swarm")


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
    for w in HeavyLiftSwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = HeavyLiftSwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "heavy-lift" / "fixtures" / "pre_lift_go.yaml"
    result = HeavyLiftSwarm().run("pre-lift-gate", yaml.safe_load(fixture.read_text()))
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

from modules.heavy_lift_swarm.swarm import HeavyLiftSwarm
from modules.heavy_lift_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = HeavyLiftSwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[heavy-lift-swarm-api] {self.address_string()} {fmt % args}")

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
        if isinstance(payload.get("LiftContextJson"), str):
            try:
                context = {**context, **json.loads(payload["LiftContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "LiftContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8096)
    args = p.parse_args()
    print(f"Heavy-lift crane swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-PICK-P12
pick_id: Panel-P12
plan:
  critical: true
  approved: true
  weight_known: true
  radius_known: true
  roles_named: true
certs:
  crane_inspection_current: true
  operator_certified: true
  rigger_qualified: true
ground:
  outriggers_set: true
  mats_ok: true
  soft_ground: false
rigging:
  inspected: true
  capacity_ok: true
  damaged: false
path:
  obstructed: false
  blind_uncontrolled: false
power_lines:
  present: true
  clearance_ok: true
  spotter_plan: true
  encroachment: false
exclusion:
  marked: true
  under_load: false
  breached: false
comms:
  signal_person: true
  channel_confirmed: true
  lost_during_critical: false
weather:
  wind_mph: 12
  wind_limit_mph: 20
  lightning: false
  poor_visibility: false
chart:
  within_chart: true
  config_match: true
  unknown_weight: false
  critical: true
taglines:
  required: true
  uncontrolled_spin: false
  riding_load: false
tandem:
  required: false
crew:
  roles:
    - lift_lead
    - crane_op
    - rigger
    - signal_person
    - spotter
    - qc_tech
    - safety_watch
  headcount: 8
  briefing_complete: true
qa:
  pre_hold_points_clear: true
  install_hold_points_clear: true
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_lift_go.yaml", go)
    write(studio / "samples" / "pre_lift_go.yaml", go)
    write(agents_root / "fixtures" / "wind_abort.yaml", """zone_id: DEMO-PICK-P12
weather:
  wind_mph: 28
  wind_limit_mph: 20
  lightning: false
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "under_load_abort.yaml", """zone_id: DEMO-PICK-P12
exclusion:
  marked: true
  under_load: true
  breached: true
comms:
  signal_person: true
  channel_confirmed: true
taglines:
  required: true
  uncontrolled_spin: false
  riding_load: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "overload_abort.yaml", """zone_id: DEMO-PICK-P12
plan:
  critical: true
  approved: true
  weight_known: false
  radius_known: true
  roles_named: true
chart:
  within_chart: false
  config_match: true
  unknown_weight: true
  critical: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "power_line_abort.yaml", """zone_id: DEMO-EAST-LOT
power_lines:
  present: true
  clearance_ok: false
  spotter_plan: false
  encroachment: true
path:
  obstructed: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "soft_ground_hold.yaml", """zone_id: DEMO-PICK-P12
ground:
  outriggers_set: false
  mats_ok: false
  soft_ground: true
certs:
  crane_inspection_current: true
  operator_certified: true
  rigger_qualified: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")

    write(ROOT / "tests" / "test_heavy_lift_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.heavy_lift_swarm.swarm import HeavyLiftSwarm
from modules.heavy_lift_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "heavy-lift" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(HeavyLiftSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_lift_go():
    assert HeavyLiftSwarm().run("pre-lift-gate", _load("pre_lift_go.yaml")).decision == "GO"


def test_wind_abort():
    assert HeavyLiftSwarm().run("weather-wind-gate", _load("wind_abort.yaml")).decision == "ABORT"


def test_under_load_abort():
    assert HeavyLiftSwarm().run("exclusion-zone-gate", _load("under_load_abort.yaml")).decision == "ABORT"


def test_overload_abort():
    assert HeavyLiftSwarm().run("load-chart-gate", _load("overload_abort.yaml")).decision == "ABORT"


def test_power_line_abort():
    assert HeavyLiftSwarm().run("power-line-clearance", _load("power_line_abort.yaml")).decision == "ABORT"


def test_soft_ground_hold():
    assert HeavyLiftSwarm().run("ground-bearing-gate", _load("soft_ground_hold.yaml")).decision == "HOLD"


def test_critical_go():
    assert HeavyLiftSwarm().run("critical-lift-runbook", _load("pre_lift_go.yaml")).decision == "GO"


def test_closeout_go():
    assert HeavyLiftSwarm().run("post-lift-closeout", _load("pre_lift_go.yaml")).decision == "GO"


def test_hold_abort():
    assert HeavyLiftSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "wind"}).decision == "ABORT"
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

### Heavy-Lift / Crane Day Swarm (Copilot Studio)

Same pattern — field GO/HOLD/ABORT for lift plans, load charts, and exclusion:

- [`copilot-studio/heavy-lift-crew/`](copilot-studio/heavy-lift-crew/) — parent + 16 child agents; open `START_HERE.md`
- Drop-in zip: [`packages/HeavyLiftCrane-Swarm-CopilotStudio-DropIn.zip`](packages/HeavyLiftCrane-Swarm-CopilotStudio-DropIn.zip)

```bash
python -m modules.heavy_lift_swarm.api --port 8096
python -m modules.heavy_lift_swarm.cli run pre-lift-gate -c agents/heavy-lift/fixtures/pre_lift_go.yaml
```
"""
        if "Heavy-Lift / Crane Day Swarm" not in rtxt and marker in rtxt:
            readme.write_text(rtxt.replace(marker, block + "\n", 1))

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "HeavyLiftCrane-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
