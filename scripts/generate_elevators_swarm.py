#!/usr/bin/env python3
"""Generate elevators / vertical transportation field swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("elevators-lead", "ElevatorsLead", "Owns elevator sequence and final GO/HOLD/ABORT.",
     """You own **elevators / vertical transportation** sequencing and assemble GO/HOLD/ABORT.

## Sequence pattern
1. Equipment submittals + shop drawings approved
2. Pit / machine room / control space ready (dimensions, waterproofing, HVAC, power)
3. Guide rails plumb; brackets; hoistway clearances
4. Entrances/doors, cab, controller, safety devices
5. Temporary run only under controlled conditions
6. AHJ / third-party inspection → turnover & training

Do not invent rail plumb readings, AHJ results, or ASME A17.1 interpretations."""),
    ("equipment-submittal", "EquipmentSubmittal", "Owns elevator equipment and shop approvals.",
     """You own elevator materials/equipment readiness.

## Checks
- Machine, controller, cab, doors, rails shops approved
- Seismic / firefighter service options per code
- Cab finishes and fixtures approved when in scope

HOLD missing approvals before rail/equipment set."""),
    ("pit-machine-room", "PitMachineRoom", "Owns pit, machine room, and control space readiness.",
     """You own pit / machine room readiness.

## Checks
- Pit dimensions, sump, waterproofing, ladder/access
- Machine room / control space size, lighting, HVAC, fire rating
- Permanent or approved temporary power available
- Smoke/heat detection per code when required

HOLD incomplete pit/MR before equipment set."""),
    ("rail-plumb", "RailPlumb", "Owns guide rail install, plumb, and brackets.",
     """You own guide rails.

## Checks
- Rail plumb/alignment within manufacturer/ASME tolerance
- Bracket spacing and anchorage
- Fishplates / joints complete

HOLD out-of-tolerance rails before cab/counterweight."""),
    ("hoistway-clearance", "HoistwayClearance", "Owns hoistway dimensions and running clearances.",
     """You own hoistway geometry.

## Checks
- Clearances to cab/CW per approved drawings
- No unauthorized projections into hoistway
- Refuge / overhead clearances met

HOLD clearance violations before run."""),
    ("door-entrance", "DoorEntrance", "Owns entrances, sills, and door operation.",
     """You own hoistway entrances.

## Checks
- Entrance frames/sills set to elevation and plumb
- Fire-rated entrances labeled where required
- Door panels/operators clear of binding

HOLD misaligned or unlabeled rated entrances."""),
    ("cab-install", "CabInstall", "Owns cab platform, sling, and finishes.",
     """You own cab installation.

## Checks
- Platform/sling square; safety plank/guides set
- Cab shell/finishes protected; weight within design
- Handrails / fixtures per shops

HOLD incomplete cab before temporary run/AHJ."""),
    ("electrical-controller", "ElectricalController", "Owns machine, controller, and wiring readiness.",
     """You own elevator electrical/controls.

## Checks
- Controller set and grounded; wiring per shops
- Machine / drive installed and aligned
- Communication / firefighter phones as required
- Disconnects labeled and accessible

HOLD incomplete electrical before energize/run."""),
    ("safety-devices", "SafetyDevices", "Owns safeties, buffers, governors, and interlocks.",
     """You own safety devices.

## Checks
- Governor, safeties, buffers installed/adjusted
- Hoistway door interlocks functional
- Emergency stop / terminal switches set
- No safety bypasses left in place

FAIL (via safety-failsafe path) if safeties bypassed for occupied use."""),
    ("ahj-inspection", "AhjInspection", "Owns AHJ / third-party inspection and permits.",
     """You own AHJ acceptance.

## Checks
- Installation permit current
- AHJ / QEI inspection scheduled or passed
- Punch from inspector dispositioned
- Certificate / temporary certificate when required

HOLD turnover without required inspection evidence."""),
    ("temporary-run", "TemporaryRun", "Owns controlled temporary construction use.",
     """You own temporary run / construction use.

## Checks
- Temporary run agreement / controls in place
- Qualified operator only; no public use
- Barricades and hoistway protection maintained
- Safety devices not defeated

HOLD/ABORT unauthorized or unsafe temporary run."""),
    ("turnover-training", "TurnoverTraining", "Owns owner training, keys, and O&M turnover.",
     """You own elevator turnover package.

## Checks
- O&M manuals, wiring diagrams, keys transferred
- Owner/staff training complete
- Maintenance contract start confirmed when required
- Warranty start documented

HOLD incomplete turnover docs/training."""),
    ("weather-protect", "WeatherProtect", "Owns hoistway dry-in and weather holds.",
     """You own environmental holds for elevator work.

## Holds
- Open hoistway exposed to weather without protection
- Machine room not weathertight when equipment set
- Freezing affecting hydraulics/oil when applicable

HOLD wet/open conditions before sensitive equipment."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work for open hoistway, fall risk, bypassed safeties.",
     """You have stop-work authority. FAIL => swarm **ABORT**.

## Fail conditions
- Open hoistway without barricades / fall protection
- Safety devices bypassed outside controlled procedure
- Unauthorized temporary run / public exposure
- Working under suspended load without secondary protection
- Confined pit entry without permit/attendant when required"""),
    ("crew-ops", "CrewOps", "Owns roles, briefing, and fatigue for elevator crews.",
     """You own crew readiness.

## Roles
elevators_lead, mechanic, helper, electrician, adjuster, qc_tech, safety_watch

HOLD missing roles, incomplete briefing, or fatigue risk."""),
    ("qa-inspector", "QaInspector", "Owns ITP hold points and elevator install records.",
     """You own elevator QA evidence.

## Checks
- Pre-install / rail / entrance hold points signed
- Plumb/clearance records attached
- NCRs closed before AHJ/turnover

HOLD missing ITP evidence."""),
]

WORKFLOWS = [
    "pre-elevator-gate",
    "pit-machine-room-gate",
    "rail-install-runbook",
    "hoistway-clearance-gate",
    "door-entrance-gate",
    "cab-controller-gate",
    "safety-devices-gate",
    "temporary-run-gate",
    "ahj-inspection-gate",
    "weather-protect-gate",
    "elevator-turnover",
    "hold-abort",
]

ROLES = (
    "elevators_lead",
    "mechanic",
    "helper",
    "electrician",
    "adjuster",
    "qc_tech",
    "safety_watch",
)

ORDERS = {
    "pre-elevator-gate": ["equipment-submittal", "pit-machine-room", "crew-ops", "weather-protect", "safety-failsafe", "qa-inspector"],
    "pit-machine-room-gate": ["pit-machine-room", "weather-protect", "qa-inspector", "safety-failsafe"],
    "rail-install-runbook": ["rail-plumb", "hoistway-clearance", "qa-inspector", "safety-failsafe"],
    "hoistway-clearance-gate": ["hoistway-clearance", "rail-plumb", "qa-inspector"],
    "door-entrance-gate": ["door-entrance", "hoistway-clearance", "qa-inspector", "safety-failsafe"],
    "cab-controller-gate": ["cab-install", "electrical-controller", "qa-inspector", "safety-failsafe"],
    "safety-devices-gate": ["safety-devices", "door-entrance", "electrical-controller", "qa-inspector", "safety-failsafe"],
    "temporary-run-gate": ["temporary-run", "safety-devices", "safety-failsafe", "qa-inspector"],
    "ahj-inspection-gate": ["ahj-inspection", "safety-devices", "hoistway-clearance", "qa-inspector", "safety-failsafe"],
    "weather-protect-gate": ["weather-protect", "pit-machine-room", "safety-failsafe"],
    "elevator-turnover": ["ahj-inspection", "turnover-training", "safety-devices", "qa-inspector", "crew-ops"],
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
    Decision: GO | HOLD | ABORT. Prefer ElevatorsContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: ElevatorsContextJson
    description: JSON context for elevators rails pit AHJ temporary run
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    ElevatorsContextJson:
      displayName: Elevators Context JSON
      description: JSON context for elevators / VTR
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
    agents_root = ROOT / "agents" / "elevators"
    studio = ROOT / "copilot-studio" / "elevators-crew"
    mod = ROOT / "modules" / "elevators_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for Elevators / VTR Swarm

From project `construction.md` extractions and typical elevator ITP practice:

- QA/QC Field Procedures – Elevator Installation (pit, rails, entrances, AHJ)
- ASME A17.1 / CSA B44 field hold-point pattern (not a code substitute)
- Temporary construction use controls and turnover/training
""")
    write(agents_root / "README.md", """# Elevators / VTR Swarm (reference twin)

> See [`../../copilot-studio/elevators-crew/`](../../copilot-studio/elevators-crew/) → `START_HERE.md`.

```bash
python -m modules.elevators_swarm.cli list
python -m modules.elevators_swarm.cli run pre-elevator-gate -c agents/elevators/fixtures/pre_elevator_go.yaml
python -m modules.elevators_swarm.api --port 8092
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# Elevators Swarm — Coordinator

Return one GO / HOLD / ABORT for elevator / VTR install.

## Hard rules
1. No rail/equipment set without pit/MR + submittals ready.
2. Rails plumb and clearances verified before run.
3. Safety devices never bypassed for occupied/temp public use.
4. AHJ evidence required before turnover.
5. SafetyFailsafe FAIL → ABORT (open hoistway, bypasses, unauthorized run).
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
  componentName: ElevatorsVtrSwarm
kind: GptComponentMetadata
displayName: Elevators VTR Swarm
instructions: |
  You are the Elevators / Vertical Transportation Swarm coordinator.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect ElevatorsContextJson; missing critical fields => HOLD (do not invent readings).
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
  - title: Pre-elevator gate
    text: Run pre-elevator-gate for Elevator Bank A and return GO/HOLD/ABORT.
  - title: Rail install
    text: Run rail-install-runbook — plumb within tolerance?
  - title: Temporary run
    text: Run temporary-run-gate before construction use.
  - title: AHJ inspection
    text: Run ahj-inspection-gate for Car 2.
  - title: Pit / machine room
    text: Run pit-machine-room-gate — ready for machine set?
  - title: Turnover
    text: Run elevator-turnover after AHJ pass.

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: Elevators VTR Swarm
schemaName: elevators_vtr_swarm
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
          - Elevators VTR Swarm ready. Ask for pre-elevator-gate, rail-install-runbook, temporary-run-gate, ahj-inspection-gate, elevator-turnover, or another named workflow. I return GO / HOLD / ABORT.
          - Elevators online — share car/bank context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.elevators_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for elevator / VTR QA gates.\n")
    write(studio / "START_HERE.md", """# START HERE — Elevators VTR Swarm drop-in

Ready Copilot Studio workspace for elevator / vertical transportation field gates.

## 3 steps
1. Open this `elevators-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Elevators VTR Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-elevator-gate…”*.

## Workflows
`pre-elevator-gate`, `pit-machine-room-gate`, `rail-install-runbook`, `hoistway-clearance-gate`, `door-entrance-gate`, `cab-controller-gate`, `safety-devices-gate`, `temporary-run-gate`, `ahj-inspection-gate`, `weather-protect-gate`, `elevator-turnover`, `hold-abort`

## Optional backend
```bash
python -m modules.elevators_swarm.api --port 8092
python -m modules.elevators_swarm.cli run pre-elevator-gate -c agents/elevators/fixtures/pre_elevator_go.yaml
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

    agents_src = r'''"""Deterministic specialist gates for elevators / VTR."""

from __future__ import annotations

from typing import Any

from modules.elevators_swarm.schemas import GateResult

ERECT_ROLES = __ROLES__


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class EquipmentSubmittalAgent:
    name = "equipment-submittal"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("equipment") or {}
        miss = _missing(m, ("shops_approved", "machine_approved", "controller_approved"))
        if miss:
            return GateResult(self.name, "HOLD", "Equipment submittals incomplete: " + ", ".join(miss), {"equipment": m})
        return GateResult(self.name, "PASS", "Elevator equipment submittals clear", {"equipment": m})


class PitMachineRoomAgent:
    name = "pit-machine-room"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("pit_mr") or {}
        miss = _missing(p, ("pit_ready", "mr_ready", "power_ready"))
        if miss:
            return GateResult(self.name, "HOLD", "Pit/MR incomplete: " + ", ".join(miss), {"pit_mr": p})
        if p.get("waterproofing_ok") is False:
            return GateResult(self.name, "HOLD", "Pit waterproofing deficient", {"pit_mr": p})
        if p.get("hvac_ok") is False:
            return GateResult(self.name, "HOLD", "Machine room HVAC/environment not ready", {"pit_mr": p})
        return GateResult(self.name, "PASS", "Pit/machine room clear", {"pit_mr": p})


class RailPlumbAgent:
    name = "rail-plumb"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        r = ctx.get("rails") or {}
        if r.get("plumb_ok") is False:
            return GateResult(self.name, "HOLD", "Guide rails out of plumb/tolerance", {"rails": r})
        if r.get("brackets_ok") is False:
            return GateResult(self.name, "HOLD", "Rail brackets/anchorage incomplete", {"rails": r})
        if not r.get("joints_ok"):
            return GateResult(self.name, "HOLD", "Rail joints/fishplates incomplete", {"rails": r})
        return GateResult(self.name, "PASS", "Rail plumb/brackets clear", {"rails": r})


class HoistwayClearanceAgent:
    name = "hoistway-clearance"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        h = ctx.get("hoistway") or {}
        if h.get("clearances_ok") is False:
            return GateResult(self.name, "HOLD", "Hoistway running clearances deficient", {"hoistway": h})
        if h.get("projections"):
            return GateResult(self.name, "HOLD", "Unauthorized projections: " + ", ".join(h["projections"]), {"hoistway": h})
        if h.get("overhead_ok") is False:
            return GateResult(self.name, "HOLD", "Overhead/refuge clearance deficient", {"hoistway": h})
        return GateResult(self.name, "PASS", "Hoistway clearances clear", {"hoistway": h})


class DoorEntranceAgent:
    name = "door-entrance"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("entrances") or {}
        if d.get("plumb_set") is False:
            return GateResult(self.name, "HOLD", "Entrances/sills not plumb/set", {"entrances": d})
        if d.get("rated_unlabeled"):
            return GateResult(self.name, "HOLD", "Fire-rated entrances unlabeled", {"entrances": d})
        if d.get("binding"):
            return GateResult(self.name, "HOLD", "Door panels/operators binding", {"entrances": d})
        return GateResult(self.name, "PASS", "Door/entrances clear", {"entrances": d})


class CabInstallAgent:
    name = "cab-install"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("cab") or {}
        if c.get("platform_ok") is False:
            return GateResult(self.name, "HOLD", "Cab platform/sling not accepted", {"cab": c})
        if c.get("overweight"):
            return GateResult(self.name, "HOLD", "Cab finishes overweight vs design", {"cab": c})
        return GateResult(self.name, "PASS", "Cab install clear", {"cab": c})


class ElectricalControllerAgent:
    name = "electrical-controller"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("electrical") or {}
        miss = _missing(e, ("controller_set", "machine_set", "disconnects_labeled"))
        if miss:
            return GateResult(self.name, "HOLD", "Electrical/controls incomplete: " + ", ".join(miss), {"electrical": e})
        if e.get("grounded") is False:
            return GateResult(self.name, "HOLD", "Controller/machine grounding incomplete", {"electrical": e})
        return GateResult(self.name, "PASS", "Electrical/controller clear", {"electrical": e})


class SafetyDevicesAgent:
    name = "safety-devices"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("devices") or {}
        if s.get("bypassed"):
            return GateResult(self.name, "FAIL", "Safety devices bypassed", {"devices": s})
        miss = _missing(s, ("governor_ok", "safeties_ok", "buffers_ok", "interlocks_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Safety devices incomplete: " + ", ".join(miss), {"devices": s})
        return GateResult(self.name, "PASS", "Safety devices clear", {"devices": s})


class AhjInspectionAgent:
    name = "ahj-inspection"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("ahj") or {}
        if not a.get("permit_current"):
            return GateResult(self.name, "HOLD", "Installation permit not current", {"ahj": a})
        if a.get("passed") is False and not a.get("scheduled"):
            return GateResult(self.name, "HOLD", "AHJ/QEI inspection not passed or scheduled", {"ahj": a})
        if a.get("open_punch"):
            return GateResult(self.name, "HOLD", "AHJ punch open: " + ", ".join(a["open_punch"]), {"ahj": a})
        if a.get("required_for_turnover") and not a.get("passed"):
            return GateResult(self.name, "HOLD", "AHJ pass required before turnover", {"ahj": a})
        return GateResult(self.name, "PASS", "AHJ/inspection clear", {"ahj": a})


class TemporaryRunAgent:
    name = "temporary-run"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("temp_run") or {}
        if t.get("unauthorized") or t.get("public_use"):
            return GateResult(self.name, "FAIL", "Unauthorized temporary run / public exposure", {"temp_run": t})
        if not t.get("agreement"):
            return GateResult(self.name, "HOLD", "Temporary run agreement/controls missing", {"temp_run": t})
        if not t.get("qualified_operator"):
            return GateResult(self.name, "HOLD", "No qualified operator for temporary run", {"temp_run": t})
        if t.get("barricades_ok") is False:
            return GateResult(self.name, "HOLD", "Hoistway barricades/protection deficient", {"temp_run": t})
        return GateResult(self.name, "PASS", "Temporary run controls clear", {"temp_run": t})


class TurnoverTrainingAgent:
    name = "turnover-training"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("turnover") or {}
        miss = _missing(t, ("om_manuals", "keys_transferred", "training_complete"))
        if miss:
            return GateResult(self.name, "HOLD", "Turnover incomplete: " + ", ".join(miss), {"turnover": t})
        return GateResult(self.name, "PASS", "Turnover/training clear", {"turnover": t})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather/environment data", {})
        holds = []
        if w.get("hoistway_open") and not w.get("protected"):
            holds.append("open hoistway without weather protection")
        if w.get("mr_not_weathertight") and w.get("equipment_set"):
            holds.append("machine room not weathertight with equipment set")
        if w.get("freezing_hydraulics"):
            holds.append("freeze risk for hydraulic oil/system")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/protection CLEAR", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("hoistway") or {}).get("unprotected_opening"):
            violations.append("open hoistway without barricades/fall protection")
        if (ctx.get("devices") or {}).get("bypassed"):
            violations.append("safety devices bypassed")
        if (ctx.get("temp_run") or {}).get("unauthorized") or (ctx.get("temp_run") or {}).get("public_use"):
            violations.append("unauthorized temporary run / public exposure")
        if (ctx.get("suspended") or {}).get("no_secondary"):
            violations.append("work under suspended load without secondary protection")
        if (ctx.get("pit_entry") or {}).get("no_permit"):
            violations.append("confined pit entry without permit/attendant")
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
            return GateResult(self.name, "PASS", "Pre-elevator QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class ElevatorsLeadAgent:
    name = "elevators-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked elevator work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('car_id', 'car'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named elevator / VTR workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.elevators_swarm.agents import (
    AhjInspectionAgent,
    CabInstallAgent,
    CrewOpsAgent,
    DoorEntranceAgent,
    ElectricalControllerAgent,
    ElevatorsLeadAgent,
    EquipmentSubmittalAgent,
    HoistwayClearanceAgent,
    PitMachineRoomAgent,
    QaInspectorAgent,
    RailPlumbAgent,
    SafetyDevicesAgent,
    SafetyFailsafeAgent,
    TemporaryRunAgent,
    TurnoverTrainingAgent,
    WeatherProtectAgent,
)
from modules.elevators_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-elevator-gate",
    "pit-machine-room-gate",
    "rail-install-runbook",
    "hoistway-clearance-gate",
    "door-entrance-gate",
    "cab-controller-gate",
    "safety-devices-gate",
    "temporary-run-gate",
    "ahj-inspection-gate",
    "weather-protect-gate",
    "elevator-turnover",
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
        return ["Proceed to next elevator sequence / workflow", "Keep plumb logs + AHJ punch current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — barricade hoistway; restore safeties; pull temp-run authority",
            "Preserve photos, plumb sheets, AHJ notes, timestamps",
            "Re-enter through pre-elevator-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "elevators-lead"]
    return [
        "Do not energize / temp-run / turn over",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("car_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.equipment = EquipmentSubmittalAgent()
        self.pit = PitMachineRoomAgent()
        self.rails = RailPlumbAgent()
        self.hoistway = HoistwayClearanceAgent()
        self.doors = DoorEntranceAgent()
        self.cab = CabInstallAgent()
        self.electrical = ElectricalControllerAgent()
        self.devices = SafetyDevicesAgent()
        self.ahj = AhjInspectionAgent()
        self.temp = TemporaryRunAgent()
        self.turnover = TurnoverTrainingAgent()
        self.weather = WeatherProtectAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = ElevatorsLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_elevator_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.equipment.evaluate(ctx),
            self.pit.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-elevator-gate", ctx, gates, {
            "GO": "Pre-elevator clear — rail/equipment sequence may proceed.",
            "HOLD": "Pre-elevator holding — equipment/pit/weather.",
            "ABORT": "Pre-elevator aborted by fail-safe.",
        })

    def pit_machine_room_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.pit.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("pit-machine-room-gate", ctx, gates, {
            "GO": "Pit/machine room clear.",
            "HOLD": "Pit/machine room holding.",
            "ABORT": "Pit/machine room aborted.",
        })

    def rail_install_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.rails.evaluate(ctx),
            self.hoistway.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("rail-install-runbook", ctx, gates, {
            "GO": "Rail install clear.",
            "HOLD": "Rail install holding.",
            "ABORT": "Rail install aborted.",
        })

    def hoistway_clearance_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.hoistway.evaluate(ctx),
            self.rails.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("hoistway-clearance-gate", ctx, gates, {
            "GO": "Hoistway clearances clear.",
            "HOLD": "Hoistway clearances holding.",
            "ABORT": "Hoistway clearances aborted.",
        })

    def door_entrance_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.doors.evaluate(ctx),
            self.hoistway.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("door-entrance-gate", ctx, gates, {
            "GO": "Door/entrances clear.",
            "HOLD": "Door/entrances holding.",
            "ABORT": "Door/entrances aborted.",
        })

    def cab_controller_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.cab.evaluate(ctx),
            self.electrical.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("cab-controller-gate", ctx, gates, {
            "GO": "Cab/controller clear.",
            "HOLD": "Cab/controller holding.",
            "ABORT": "Cab/controller aborted.",
        })

    def safety_devices_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.devices.evaluate(ctx),
            self.doors.evaluate(ctx),
            self.electrical.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("safety-devices-gate", ctx, gates, {
            "GO": "Safety devices clear.",
            "HOLD": "Safety devices holding.",
            "ABORT": "Safety devices aborted — restore safeties.",
        })

    def temporary_run_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.temp.evaluate(ctx),
            self.devices.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("temporary-run-gate", ctx, gates, {
            "GO": "Temporary run controls clear.",
            "HOLD": "Temporary run holding.",
            "ABORT": "Temporary run aborted.",
        })

    def ahj_inspection_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.ahj.evaluate(ctx),
            self.devices.evaluate(ctx),
            self.hoistway.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("ahj-inspection-gate", ctx, gates, {
            "GO": "AHJ inspection path clear.",
            "HOLD": "AHJ inspection holding.",
            "ABORT": "AHJ inspection aborted.",
        })

    def weather_protect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.weather.evaluate(ctx),
            self.pit.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish("weather-protect-gate", ctx, gates, {
            "GO": "Weather/protection clear.",
            "HOLD": "Weather holding.",
            "ABORT": "Weather aborted.",
        })

    def elevator_turnover(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "ahj": {**(ctx.get("ahj") or {}), "required_for_turnover": True}}
        gates = [
            self.ahj.evaluate(ctx),
            self.turnover.evaluate(ctx),
            self.devices.evaluate(ctx),
            self.qa.evaluate(ctx, phase="closeout"),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("elevator-turnover", ctx, gates, {
            "GO": "Elevator turnover clear.",
            "HOLD": "Elevator turnover holding.",
            "ABORT": "Elevator turnover aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "elevators-lead",
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

    write(mod / "swarm.py", '''"""Elevators / VTR swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.elevators_swarm.schemas import SwarmResult
from modules.elevators_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class ElevatorsSwarm:
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
        log_event(f"[elevators-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[elevators-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["ElevatorsSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.elevators_swarm.swarm import ElevatorsSwarm, SwarmResult
from modules.elevators_swarm.workflows import WORKFLOW_IDS

__all__ = ["ElevatorsSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for elevators / VTR swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.elevators_swarm.swarm import ElevatorsSwarm

app = typer.Typer(add_completion=False, help="Elevators / VTR field swarm")


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
    for w in ElevatorsSwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = ElevatorsSwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "elevators" / "fixtures" / "pre_elevator_go.yaml"
    result = ElevatorsSwarm().run("pre-elevator-gate", yaml.safe_load(fixture.read_text()))
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

from modules.elevators_swarm.swarm import ElevatorsSwarm
from modules.elevators_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = ElevatorsSwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[elevators-swarm-api] {self.address_string()} {fmt % args}")

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
        if isinstance(payload.get("ElevatorsContextJson"), str):
            try:
                context = {**context, **json.loads(payload["ElevatorsContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "ElevatorsContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8092)
    args = p.parse_args()
    print(f"Elevators VTR swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-BANK-A-CAR2
car_id: Car-2
equipment:
  shops_approved: true
  machine_approved: true
  controller_approved: true
pit_mr:
  pit_ready: true
  mr_ready: true
  power_ready: true
  waterproofing_ok: true
  hvac_ok: true
rails:
  plumb_ok: true
  brackets_ok: true
  joints_ok: true
hoistway:
  clearances_ok: true
  projections: []
  overhead_ok: true
  unprotected_opening: false
entrances:
  plumb_set: true
  rated_unlabeled: false
  binding: false
cab:
  platform_ok: true
  overweight: false
electrical:
  controller_set: true
  machine_set: true
  disconnects_labeled: true
  grounded: true
devices:
  governor_ok: true
  safeties_ok: true
  buffers_ok: true
  interlocks_ok: true
  bypassed: false
ahj:
  permit_current: true
  scheduled: true
  passed: true
  open_punch: []
  required_for_turnover: true
temp_run:
  agreement: true
  qualified_operator: true
  barricades_ok: true
  unauthorized: false
  public_use: false
turnover:
  om_manuals: true
  keys_transferred: true
  training_complete: true
weather:
  hoistway_open: false
  protected: true
  mr_not_weathertight: false
  equipment_set: true
  freezing_hydraulics: false
crew:
  roles:
    - elevators_lead
    - mechanic
    - helper
    - electrician
    - adjuster
    - qc_tech
    - safety_watch
  headcount: 8
  briefing_complete: true
  fatigued_workers: []
qa:
  pre_hold_points_clear: true
  install_hold_points_clear: true
suspended:
  no_secondary: false
pit_entry:
  no_permit: false
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_elevator_go.yaml", go)
    write(studio / "samples" / "pre_elevator_go.yaml", go)
    write(agents_root / "fixtures" / "rails_out_hold.yaml", """zone_id: DEMO-BANK-A-CAR2
rails:
  plumb_ok: false
  brackets_ok: false
  joints_ok: true
hoistway:
  clearances_ok: false
  projections: [conduit_clamp]
  overhead_ok: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "open_hoistway_abort.yaml", """zone_id: DEMO-BANK-A-CAR2
hoistway:
  clearances_ok: true
  overhead_ok: true
  unprotected_opening: true
rails:
  plumb_ok: true
  brackets_ok: true
  joints_ok: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "safety_bypass_abort.yaml", """zone_id: DEMO-BANK-A-CAR2
devices:
  governor_ok: true
  safeties_ok: true
  buffers_ok: true
  interlocks_ok: false
  bypassed: true
temp_run:
  agreement: false
  qualified_operator: false
  barricades_ok: false
  unauthorized: true
  public_use: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "ahj_punch_hold.yaml", """zone_id: DEMO-BANK-A-CAR2
ahj:
  permit_current: true
  scheduled: true
  passed: false
  open_punch: [sill_gap, phone_test]
  required_for_turnover: true
devices:
  governor_ok: true
  safeties_ok: true
  buffers_ok: true
  interlocks_ok: true
  bypassed: false
hoistway:
  clearances_ok: true
  overhead_ok: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "pit_not_ready_hold.yaml", """zone_id: DEMO-BANK-A-CAR2
equipment:
  shops_approved: true
  machine_approved: true
  controller_approved: true
pit_mr:
  pit_ready: false
  mr_ready: false
  power_ready: false
  waterproofing_ok: false
  hvac_ok: false
weather:
  hoistway_open: true
  protected: false
  mr_not_weathertight: true
  equipment_set: false
crew:
  roles: [elevators_lead, mechanic, helper, electrician, adjuster, qc_tech, safety_watch]
  briefing_complete: true
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")

    write(ROOT / "tests" / "test_elevators_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.elevators_swarm.swarm import ElevatorsSwarm
from modules.elevators_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "elevators" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(ElevatorsSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_elevator_go():
    assert ElevatorsSwarm().run("pre-elevator-gate", _load("pre_elevator_go.yaml")).decision == "GO"


def test_rails_out_hold():
    assert ElevatorsSwarm().run("rail-install-runbook", _load("rails_out_hold.yaml")).decision == "HOLD"


def test_open_hoistway_abort():
    assert ElevatorsSwarm().run("rail-install-runbook", _load("open_hoistway_abort.yaml")).decision == "ABORT"


def test_safety_bypass_abort():
    assert ElevatorsSwarm().run("temporary-run-gate", _load("safety_bypass_abort.yaml")).decision == "ABORT"


def test_ahj_punch_hold():
    assert ElevatorsSwarm().run("ahj-inspection-gate", _load("ahj_punch_hold.yaml")).decision == "HOLD"


def test_pit_not_ready_hold():
    assert ElevatorsSwarm().run("pre-elevator-gate", _load("pit_not_ready_hold.yaml")).decision == "HOLD"


def test_turnover_go():
    assert ElevatorsSwarm().run("elevator-turnover", _load("pre_elevator_go.yaml")).decision == "GO"


def test_safety_devices_go():
    assert ElevatorsSwarm().run("safety-devices-gate", _load("pre_elevator_go.yaml")).decision == "GO"


def test_hold_abort():
    assert ElevatorsSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "open hoistway"}).decision == "ABORT"
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

### Elevators / VTR Swarm (Copilot Studio)

Same pattern — field GO/HOLD/ABORT for elevators and vertical transportation:

- [`copilot-studio/elevators-crew/`](copilot-studio/elevators-crew/) — parent + 16 child agents; open `START_HERE.md`
- Drop-in zip: [`packages/ElevatorsVTR-Swarm-CopilotStudio-DropIn.zip`](packages/ElevatorsVTR-Swarm-CopilotStudio-DropIn.zip)

```bash
python -m modules.elevators_swarm.api --port 8092
python -m modules.elevators_swarm.cli run pre-elevator-gate -c agents/elevators/fixtures/pre_elevator_go.yaml
```
"""
        if "Elevators / VTR Swarm" not in rtxt and marker in rtxt:
            readme.write_text(rtxt.replace(marker, block + "\n", 1))

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "ElevatorsVTR-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
