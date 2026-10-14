#!/usr/bin/env python3
"""Generate daily safety / hot work / confined space field swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("safety-lead", "SafetyLead", "Owns daily safety sequence and final GO/HOLD/ABORT.",
     """You own **daily site safety** (permits, hot work, confined space, LOTO, fall protection) and assemble GO/HOLD/ABORT.

## Sequence pattern
1. Pre-shift briefing + PPE + competent persons named
2. Permits issued before high-risk work (hot work, CSE, LOTO)
3. Controls verified in field (fire watch, attendant, gas tests, PFAS)
4. Mid-shift weather/emergency holds
5. Close permits; end-of-shift hazards secured

Do not invent gas readings, permit numbers, or medical advice."""),
    ("daily-briefing", "DailyBriefing", "Owns JHA/toolbox talk and task hazards.",
     """You own pre-shift briefing.

## Checks
- Toolbox / JHA completed for today's tasks
- High-risk activities called out (hot work, CSE, heights, excavate)
- Emergency muster / radio channels confirmed

HOLD crews starting without briefing for the task."""),
    ("ppe-readiness", "PpeReadiness", "Owns required PPE for the task and zone.",
     """You own PPE readiness.

## Checks
- Task PPE available (hard hat, eye, gloves, FR, harness, respirator as required)
- Damaged/expired PPE removed from service
- Specialty PPE fit-tested when required

HOLD missing required PPE for the task."""),
    ("hot-work-permit", "HotWorkPermit", "Owns hot work permits and area prep.",
     """You own hot work authorization.

## Checks
- Permit issued for location/time window
- Combustibles removed/protected; sprinklers/detection status known
- Fire extinguisher staged; fire watch assigned
- Hot work paused if permit conditions break

FAIL/ABORT hot work without valid permit."""),
    ("fire-watch", "FireWatch", "Owns fire watch during and after hot work.",
     """You own fire watch.

## Checks
- Fire watch present during hot work
- Post-watch duration met (often 30–60 min)
- Extinguisher accessible; radio/alarm path known

HOLD closing hot work area before post-watch complete."""),
    ("confined-space", "ConfinedSpace", "Owns CSE permits, gas tests, and attendant.",
     """You own confined space entry.

## Checks
- Space classified; entry permit issued
- Atmospheric tests current (O2, LEL, toxics)
- Attendant present; rescue plan ready
- Entrants logged in/out

FAIL/ABORT entry without permit/attendant/gas clear."""),
    ("loto-energy", "LotoEnergy", "Owns lockout/tagout and zero-energy verification.",
     """You own LOTO / energy isolation.

## Checks
- LOTO procedure for equipment applied
- Locks/tags on all energy sources
- Zero-energy verified before work
- Group LOTO / multi-craft coordination when needed

HOLD/FAIL work on energized equipment without LOTO."""),
    ("fall-protection", "FallProtection", "Owns PFAS, guardrails, and hole covers.",
     """You own fall protection.

## Checks
- Guardrails / covers / PFAS for work ≥ threshold
- Anchorage rated; harness inspected
- Leading edges controlled; floor holes covered/marked

FAIL unprotected work at height / open holes."""),
    ("excavation-competent", "ExcavationCompetent", "Owns excavation competent person and trench safety.",
     """You own excavation safety.

## Checks
- Competent person named for excavate/trench
- Protective system (slope/shore/shield) as required
- Spoil setbacks; access/egress; atmosphere if deep

HOLD/FAIL unprotected trench entry."""),
    ("crane-exclusion", "CraneExclusion", "Owns lift exclusion zones and tag lines.",
     """You own crane/lift exclusion.

## Checks
- Exclusion zone marked; signal person identified
- No unauthorized entry under load
- Power line clearances observed

FAIL entry under suspended load / breached exclusion."""),
    ("incident-stop", "IncidentStop", "Owns stop-work and incident scene control.",
     """You own incident / stop-work response.

## Checks
- Stop-work authority honored
- Scene secured; first aid / emergency services as needed
- Evidence preserved; notifications started

ABORT continuing work after unresolved stop-work/incident."""),
    ("weather-emergency", "WeatherEmergency", "Owns weather and site emergency holds.",
     """You own weather/emergency holds.

## Holds
- Lightning / high wind for exposed work and cranes
- Extreme heat/cold without controls
- Site emergency alarm / evacuate

HOLD or ABORT per severity."""),
    ("substance-fatigue", "SubstanceFatigue", "Owns impairment and fatigue risk flags.",
     """You own impairment/fatigue screening flags.

## Checks
- Observed impairment => remove from safety-sensitive work
- Fatigue risk on night/extended shifts flagged
- No punitive medical diagnosis — field observation + supervisor action only

HOLD safety-sensitive tasks when impairment/fatigue flagged."""),
    ("safety-failsafe", "SafetyFailsafe", "Hard stop-work authority for life-critical violations.",
     """You have stop-work authority. FAIL => swarm **ABORT**.

## Fail conditions
- Hot work without permit / fire watch
- Confined space entry without permit, attendant, or clear gas tests
- Unprotected work at height or open holes
- Energized work without LOTO
- Continuing after stop-work / serious incident
- Personnel under suspended load"""),
    ("crew-ops", "CrewOps", "Owns safety staffing roles and headcount.",
     """You own safety staffing.

## Roles
safety_lead, supervisor, fire_watch, cse_attendant, competent_person, first_aid, qc_tech

HOLD missing required safety roles for the permitted work."""),
    ("qa-inspector", "QaInspector", "Owns permit logs and safety documentation.",
     """You own safety documentation.

## Checks
- Permits posted/logged with times and names
- Gas tests / LOTO sheets attached
- Closeout signatures complete

HOLD missing permit documentation for claimed authorization."""),
]

WORKFLOWS = [
    "pre-shift-safety-gate",
    "hot-work-permit-gate",
    "confined-space-entry",
    "loto-release-gate",
    "fall-protection-gate",
    "excavation-safety-gate",
    "crane-exclusion-gate",
    "fire-watch-closeout",
    "incident-abort",
    "weather-emergency-gate",
    "end-of-shift-closeout",
    "hold-abort",
]

ROLES = (
    "safety_lead",
    "supervisor",
    "fire_watch",
    "cse_attendant",
    "competent_person",
    "first_aid",
    "qc_tech",
)

ORDERS = {
    "pre-shift-safety-gate": ["daily-briefing", "ppe-readiness", "substance-fatigue", "crew-ops", "weather-emergency", "safety-failsafe", "qa-inspector"],
    "hot-work-permit-gate": ["hot-work-permit", "fire-watch", "ppe-readiness", "qa-inspector", "safety-failsafe"],
    "confined-space-entry": ["confined-space", "ppe-readiness", "crew-ops", "qa-inspector", "safety-failsafe"],
    "loto-release-gate": ["loto-energy", "qa-inspector", "safety-failsafe"],
    "fall-protection-gate": ["fall-protection", "ppe-readiness", "qa-inspector", "safety-failsafe"],
    "excavation-safety-gate": ["excavation-competent", "ppe-readiness", "qa-inspector", "safety-failsafe"],
    "crane-exclusion-gate": ["crane-exclusion", "crew-ops", "safety-failsafe", "qa-inspector"],
    "fire-watch-closeout": ["fire-watch", "hot-work-permit", "qa-inspector"],
    "incident-abort": ["incident-stop", "safety-failsafe"],
    "weather-emergency-gate": ["weather-emergency", "safety-failsafe"],
    "end-of-shift-closeout": ["qa-inspector", "hot-work-permit", "confined-space", "loto-energy", "crew-ops"],
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
    Decision: GO | HOLD | ABORT. Prefer SafetyContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: SafetyContextJson
    description: JSON context for daily safety permits hot work CSE LOTO
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    SafetyContextJson:
      displayName: Safety Context JSON
      description: JSON context for daily safety / permits
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
    agents_root = ROOT / "agents" / "daily-safety"
    studio = ROOT / "copilot-studio" / "daily-safety-crew"
    mod = ROOT / "modules" / "daily_safety_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for Daily Safety Swarm

From project `construction.md` extractions and typical site EHS permit practice:

- Daily briefing / JHA and PPE readiness
- Hot work permit + fire watch
- Confined space entry (permit, gas tests, attendant)
- LOTO, fall protection, excavation competent person, crane exclusion
""")
    write(agents_root / "README.md", """# Daily Safety Swarm (reference twin)

> See [`../../copilot-studio/daily-safety-crew/`](../../copilot-studio/daily-safety-crew/) → `START_HERE.md`.

```bash
python -m modules.daily_safety_swarm.cli list
python -m modules.daily_safety_swarm.cli run pre-shift-safety-gate -c agents/daily-safety/fixtures/pre_shift_go.yaml
python -m modules.daily_safety_swarm.api --port 8095
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# Daily Safety Swarm — Coordinator

Return one GO / HOLD / ABORT for daily site safety permits and controls.

## Hard rules
1. No hot work / CSE / energized work without valid permits and controls.
2. Fall protection and trench protection before exposure.
3. Stop-work and incidents override production.
4. Fire watch / attendant / gas tests are not optional when required.
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
  componentName: DailySafetySwarm
kind: GptComponentMetadata
displayName: Daily Safety Swarm
instructions: |
  You are the Daily Safety / Hot Work / Confined Space Swarm coordinator.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect SafetyContextJson; missing critical fields => HOLD (do not invent readings).
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
  - title: Pre-shift safety
    text: Run pre-shift-safety-gate for Tower crane day and return GO/HOLD/ABORT.
  - title: Hot work permit
    text: Run hot-work-permit-gate for welding on Level 5.
  - title: Confined space
    text: Run confined-space-entry for Tank T-2.
  - title: LOTO
    text: Run loto-release-gate before MCC work.
  - title: Fall protection
    text: Run fall-protection-gate for deck edge work.
  - title: Incident abort
    text: Run incident-abort — stop-work called after near miss.

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: Daily Safety Swarm
schemaName: daily_safety_swarm
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
          - Daily Safety Swarm ready. Ask for pre-shift-safety-gate, hot-work-permit-gate, confined-space-entry, loto-release-gate, fall-protection-gate, or another named workflow. I return GO / HOLD / ABORT.
          - Safety online — share task/permit context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.daily_safety_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for daily safety permits and life-critical controls.\n")
    write(studio / "START_HERE.md", """# START HERE — Daily Safety Swarm drop-in

Ready Copilot Studio workspace for daily safety / hot work / confined space gates.

## 3 steps
1. Open this `daily-safety-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Daily Safety Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-shift-safety-gate…”*.

## Workflows
`pre-shift-safety-gate`, `hot-work-permit-gate`, `confined-space-entry`, `loto-release-gate`, `fall-protection-gate`, `excavation-safety-gate`, `crane-exclusion-gate`, `fire-watch-closeout`, `incident-abort`, `weather-emergency-gate`, `end-of-shift-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.daily_safety_swarm.api --port 8095
python -m modules.daily_safety_swarm.cli run pre-shift-safety-gate -c agents/daily-safety/fixtures/pre_shift_go.yaml
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

    agents_src = r'''"""Deterministic specialist gates for daily safety."""

from __future__ import annotations

from typing import Any

from modules.daily_safety_swarm.schemas import GateResult

ERECT_ROLES = __ROLES__


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class DailyBriefingAgent:
    name = "daily-briefing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("briefing") or {}
        if not b.get("complete"):
            return GateResult(self.name, "HOLD", "Pre-shift briefing/JHA incomplete", {"briefing": b})
        if not b.get("high_risk_called_out") and b.get("has_high_risk"):
            return GateResult(self.name, "HOLD", "High-risk tasks not covered in briefing", {"briefing": b})
        return GateResult(self.name, "PASS", "Daily briefing clear", {"briefing": b})


class PpeReadinessAgent:
    name = "ppe-readiness"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("ppe") or {}
        if p.get("missing"):
            return GateResult(self.name, "HOLD", "Missing PPE: " + ", ".join(p["missing"]), {"ppe": p})
        if p.get("damaged_in_use"):
            return GateResult(self.name, "HOLD", "Damaged/expired PPE in use", {"ppe": p})
        return GateResult(self.name, "PASS", "PPE readiness clear", {"ppe": p})


class HotWorkPermitAgent:
    name = "hot-work-permit"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        h = ctx.get("hot_work") or {}
        if h.get("required") is False:
            return GateResult(self.name, "SKIP", "No hot work", {})
        if h.get("no_permit") or not h.get("permit_valid"):
            return GateResult(self.name, "FAIL", "Hot work without valid permit", {"hot_work": h})
        if h.get("combustibles_cleared") is False:
            return GateResult(self.name, "HOLD", "Combustibles not cleared/protected", {"hot_work": h})
        if not h.get("extinguisher_staged"):
            return GateResult(self.name, "HOLD", "Fire extinguisher not staged", {"hot_work": h})
        return GateResult(self.name, "PASS", "Hot work permit clear", {"hot_work": h})


class FireWatchAgent:
    name = "fire-watch"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("fire_watch") or {}
        if f.get("required") is False:
            return GateResult(self.name, "SKIP", "No fire watch required", {})
        if not f.get("present_during"):
            return GateResult(self.name, "FAIL", "Fire watch not present during hot work", {"fire_watch": f})
        if f.get("post_watch_complete") is False:
            return GateResult(self.name, "HOLD", "Post hot-work fire watch not complete", {"fire_watch": f})
        return GateResult(self.name, "PASS", "Fire watch clear", {"fire_watch": f})


class ConfinedSpaceAgent:
    name = "confined-space"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("cse") or {}
        if c.get("required") is False:
            return GateResult(self.name, "SKIP", "No confined space entry", {})
        if not c.get("permit_valid"):
            return GateResult(self.name, "FAIL", "CSE without valid entry permit", {"cse": c})
        if not c.get("attendant_present"):
            return GateResult(self.name, "FAIL", "CSE attendant not present", {"cse": c})
        if c.get("gas_clear") is False:
            return GateResult(self.name, "FAIL", "Atmosphere not clear / tests failed", {"cse": c})
        if not c.get("rescue_plan"):
            return GateResult(self.name, "HOLD", "Rescue plan not confirmed", {"cse": c})
        return GateResult(self.name, "PASS", "Confined space entry clear", {"cse": c})


class LotoEnergyAgent:
    name = "loto-energy"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("loto") or {}
        if l.get("required") is False:
            return GateResult(self.name, "SKIP", "No LOTO this gate", {})
        if not l.get("applied"):
            return GateResult(self.name, "FAIL", "LOTO not applied for energized work", {"loto": l})
        if l.get("zero_energy_verified") is False:
            return GateResult(self.name, "FAIL", "Zero-energy not verified", {"loto": l})
        return GateResult(self.name, "PASS", "LOTO clear", {"loto": l})


class FallProtectionAgent:
    name = "fall-protection"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("fall") or {}
        if f.get("required") is False:
            return GateResult(self.name, "SKIP", "No fall exposure", {})
        if f.get("unprotected"):
            return GateResult(self.name, "FAIL", "Unprotected work at height / open holes", {"fall": f})
        if f.get("harness_ok") is False or f.get("anchorage_ok") is False:
            return GateResult(self.name, "HOLD", "PFAS/anchorage deficient", {"fall": f})
        return GateResult(self.name, "PASS", "Fall protection clear", {"fall": f})


class ExcavationCompetentAgent:
    name = "excavation-competent"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("excavation") or {}
        if e.get("required") is False:
            return GateResult(self.name, "SKIP", "No excavation", {})
        if not e.get("competent_person"):
            return GateResult(self.name, "HOLD", "Excavation competent person not named", {"excavation": e})
        if e.get("unprotected_trench"):
            return GateResult(self.name, "FAIL", "Unprotected trench/excavation", {"excavation": e})
        return GateResult(self.name, "PASS", "Excavation safety clear", {"excavation": e})


class CraneExclusionAgent:
    name = "crane-exclusion"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("crane") or {}
        if c.get("required") is False:
            return GateResult(self.name, "SKIP", "No crane/lift", {})
        if c.get("under_load"):
            return GateResult(self.name, "FAIL", "Personnel under suspended load / exclusion breached", {"crane": c})
        if not c.get("exclusion_marked") or not c.get("signal_person"):
            return GateResult(self.name, "HOLD", "Exclusion zone/signal person incomplete", {"crane": c})
        return GateResult(self.name, "PASS", "Crane exclusion clear", {"crane": c})


class IncidentStopAgent:
    name = "incident-stop"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        i = ctx.get("incident") or {}
        if i.get("stop_work") or i.get("serious_incident"):
            if i.get("continuing"):
                return GateResult(self.name, "FAIL", "Work continuing after stop-work/incident", {"incident": i})
            return GateResult(self.name, "FAIL", "Stop-work / incident — secure scene", {"incident": i})
        return GateResult(self.name, "PASS", "No active incident/stop-work", {"incident": i})


class WeatherEmergencyAgent:
    name = "weather-emergency"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if w.get("site_evacuate"):
            return GateResult(self.name, "FAIL", "Site emergency — evacuate", {"weather": w})
        holds = []
        if w.get("lightning") or w.get("high_wind"):
            holds.append("lightning/high wind — exposed/crane hold")
        if w.get("extreme_temp") and not w.get("controls"):
            holds.append("extreme temperature without controls")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/emergency CLEAR", {"weather": w})


class SubstanceFatigueAgent:
    name = "substance-fatigue"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("impairment") or {}
        if s.get("observed_impairment"):
            return GateResult(self.name, "HOLD", "Observed impairment — remove from safety-sensitive work", {"impairment": s})
        if s.get("fatigue_risk"):
            return GateResult(self.name, "HOLD", "Fatigue risk flagged for safety-sensitive tasks", {"impairment": s})
        return GateResult(self.name, "PASS", "No impairment/fatigue flags", {"impairment": s})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        hw = ctx.get("hot_work") or {}
        if hw.get("required") is not False and (hw.get("no_permit") or hw.get("permit_valid") is False):
            violations.append("hot work without permit")
        if (ctx.get("fire_watch") or {}).get("required") is not False and (ctx.get("fire_watch") or {}).get("present_during") is False and hw.get("active"):
            violations.append("fire watch missing during hot work")
        cse = ctx.get("cse") or {}
        if cse.get("required") and (not cse.get("permit_valid") or not cse.get("attendant_present") or cse.get("gas_clear") is False):
            violations.append("unsafe confined space entry")
        if (ctx.get("fall") or {}).get("unprotected"):
            violations.append("unprotected fall exposure")
        if (ctx.get("loto") or {}).get("required") and not (ctx.get("loto") or {}).get("applied"):
            violations.append("energized work without LOTO")
        if (ctx.get("incident") or {}).get("stop_work") and (ctx.get("incident") or {}).get("continuing"):
            violations.append("continuing after stop-work")
        if (ctx.get("crane") or {}).get("under_load"):
            violations.append("personnel under suspended load")
        if (ctx.get("excavation") or {}).get("unprotected_trench"):
            violations.append("unprotected trench")
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
            return GateResult(self.name, "HOLD", "Crew briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Safety staffing ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-shift safety docs clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} permit docs clear", {})
        return GateResult(self.name, "HOLD", f"No safety QA evidence for phase={phase}", {"qa": q})


class SafetyLeadAgent:
    name = "safety-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked unsafe work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Safety sequence ready for {ctx.get('zone_id', ctx.get('task', 'task'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named daily safety workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.daily_safety_swarm.agents import (
    ConfinedSpaceAgent,
    CraneExclusionAgent,
    CrewOpsAgent,
    DailyBriefingAgent,
    ExcavationCompetentAgent,
    FallProtectionAgent,
    FireWatchAgent,
    HotWorkPermitAgent,
    IncidentStopAgent,
    LotoEnergyAgent,
    PpeReadinessAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SafetyLeadAgent,
    SubstanceFatigueAgent,
    WeatherEmergencyAgent,
)
from modules.daily_safety_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-shift-safety-gate",
    "hot-work-permit-gate",
    "confined-space-entry",
    "loto-release-gate",
    "fall-protection-gate",
    "excavation-safety-gate",
    "crane-exclusion-gate",
    "fire-watch-closeout",
    "incident-abort",
    "weather-emergency-gate",
    "end-of-shift-closeout",
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
        return ["Proceed with permitted work under listed controls", "Keep permits posted; re-check if conditions change"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — make area safe; pull permits if violated",
            "Preserve permit sheets, gas logs, photos, timestamps",
            "Re-enter through pre-shift-safety-gate / specific permit gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "safety-lead"]
    return [
        "Do not start/continue high-risk task until cleared",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("task") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.briefing = DailyBriefingAgent()
        self.ppe = PpeReadinessAgent()
        self.hot = HotWorkPermitAgent()
        self.fire = FireWatchAgent()
        self.cse = ConfinedSpaceAgent()
        self.loto = LotoEnergyAgent()
        self.fall = FallProtectionAgent()
        self.excavation = ExcavationCompetentAgent()
        self.crane = CraneExclusionAgent()
        self.incident = IncidentStopAgent()
        self.weather = WeatherEmergencyAgent()
        self.impairment = SubstanceFatigueAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = SafetyLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_shift_safety_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.briefing.evaluate(ctx),
            self.ppe.evaluate(ctx),
            self.impairment.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-shift-safety-gate", ctx, gates, {
            "GO": "Pre-shift safety clear — permitted work may proceed under controls.",
            "HOLD": "Pre-shift safety holding — briefing/PPE/weather.",
            "ABORT": "Pre-shift aborted by fail-safe.",
        })

    def hot_work_permit_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {
            **ctx,
            "hot_work": {**(ctx.get("hot_work") or {}), "required": True, "active": True},
            "fire_watch": {**(ctx.get("fire_watch") or {}), "required": True},
        }
        gates = [
            self.hot.evaluate(ctx),
            self.fire.evaluate(ctx),
            self.ppe.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("hot-work-permit-gate", ctx, gates, {
            "GO": "Hot work permit clear.",
            "HOLD": "Hot work holding.",
            "ABORT": "Hot work aborted — stop welding/cutting.",
        })

    def confined_space_entry(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "cse": {**(ctx.get("cse") or {}), "required": True}}
        gates = [
            self.cse.evaluate(ctx),
            self.ppe.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("confined-space-entry", ctx, gates, {
            "GO": "Confined space entry clear.",
            "HOLD": "Confined space holding.",
            "ABORT": "Confined space aborted — evacuate/stop entry.",
        })

    def loto_release_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "loto": {**(ctx.get("loto") or {}), "required": True}}
        gates = [
            self.loto.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("loto-release-gate", ctx, gates, {
            "GO": "LOTO clear for work.",
            "HOLD": "LOTO holding.",
            "ABORT": "LOTO aborted — do not touch equipment.",
        })

    def fall_protection_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "fall": {**(ctx.get("fall") or {}), "required": True}}
        gates = [
            self.fall.evaluate(ctx),
            self.ppe.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("fall-protection-gate", ctx, gates, {
            "GO": "Fall protection clear.",
            "HOLD": "Fall protection holding.",
            "ABORT": "Fall protection aborted.",
        })

    def excavation_safety_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "excavation": {**(ctx.get("excavation") or {}), "required": True}}
        gates = [
            self.excavation.evaluate(ctx),
            self.ppe.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("excavation-safety-gate", ctx, gates, {
            "GO": "Excavation safety clear.",
            "HOLD": "Excavation safety holding.",
            "ABORT": "Excavation safety aborted.",
        })

    def crane_exclusion_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "crane": {**(ctx.get("crane") or {}), "required": True}}
        gates = [
            self.crane.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("crane-exclusion-gate", ctx, gates, {
            "GO": "Crane exclusion clear.",
            "HOLD": "Crane exclusion holding.",
            "ABORT": "Crane exclusion aborted.",
        })

    def fire_watch_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {
            **ctx,
            "hot_work": {**(ctx.get("hot_work") or {}), "required": True},
            "fire_watch": {**(ctx.get("fire_watch") or {}), "required": True},
        }
        gates = [
            self.fire.evaluate(ctx),
            self.hot.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("fire-watch-closeout", ctx, gates, {
            "GO": "Fire watch closeout clear.",
            "HOLD": "Fire watch closeout holding.",
            "ABORT": "Fire watch closeout aborted.",
        })

    def incident_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "incident": {**(ctx.get("incident") or {}), "stop_work": True}}
        gates = [self.incident.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("incident-abort", ctx, gates, {
            "GO": "No incident path (unexpected).",
            "HOLD": "Incident holding.",
            "ABORT": "Incident/stop-work — secure scene.",
        })

    def weather_emergency_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-emergency-gate", ctx, gates, {
            "GO": "Weather/emergency clear.",
            "HOLD": "Weather holding.",
            "ABORT": "Emergency — evacuate/stop.",
        })

    def end_of_shift_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="closeout"),
            self.hot.evaluate(ctx),
            self.cse.evaluate(ctx),
            self.loto.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("end-of-shift-closeout", ctx, gates, {
            "GO": "End-of-shift safety closeout clear.",
            "HOLD": "End-of-shift closeout holding.",
            "ABORT": "End-of-shift closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "safety-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "site_safety")},
        )]
        summary = "ABORT escalated — stop work and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
''')

    write(mod / "swarm.py", '''"""Daily safety swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.daily_safety_swarm.schemas import SwarmResult
from modules.daily_safety_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class DailySafetySwarm:
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
        log_event(f"[daily-safety-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[daily-safety-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["DailySafetySwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.daily_safety_swarm.swarm import DailySafetySwarm, SwarmResult
from modules.daily_safety_swarm.workflows import WORKFLOW_IDS

__all__ = ["DailySafetySwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for daily safety swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.daily_safety_swarm.swarm import DailySafetySwarm

app = typer.Typer(add_completion=False, help="Daily safety / hot work / CSE field swarm")


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
    for w in DailySafetySwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = DailySafetySwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "daily-safety" / "fixtures" / "pre_shift_go.yaml"
    result = DailySafetySwarm().run("pre-shift-safety-gate", yaml.safe_load(fixture.read_text()))
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

from modules.daily_safety_swarm.swarm import DailySafetySwarm
from modules.daily_safety_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = DailySafetySwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[daily-safety-swarm-api] {self.address_string()} {fmt % args}")

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
        if isinstance(payload.get("SafetyContextJson"), str):
            try:
                context = {**context, **json.loads(payload["SafetyContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "SafetyContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8095)
    args = p.parse_args()
    print(f"Daily safety swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-SITE-DAY
task: Tower day + Level 5 weld
briefing:
  complete: true
  has_high_risk: true
  high_risk_called_out: true
ppe:
  missing: []
  damaged_in_use: false
hot_work:
  required: true
  permit_valid: true
  no_permit: false
  combustibles_cleared: true
  extinguisher_staged: true
  active: false
fire_watch:
  required: true
  present_during: true
  post_watch_complete: true
cse:
  required: false
loto:
  required: false
fall:
  required: true
  unprotected: false
  harness_ok: true
  anchorage_ok: true
excavation:
  required: false
crane:
  required: true
  exclusion_marked: true
  signal_person: true
  under_load: false
incident:
  stop_work: false
  serious_incident: false
  continuing: false
weather:
  lightning: false
  high_wind: false
  extreme_temp: false
  controls: true
  site_evacuate: false
impairment:
  observed_impairment: false
  fatigue_risk: false
crew:
  roles:
    - safety_lead
    - supervisor
    - fire_watch
    - cse_attendant
    - competent_person
    - first_aid
    - qc_tech
  headcount: 14
  briefing_complete: true
qa:
  pre_hold_points_clear: true
  install_hold_points_clear: true
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_shift_go.yaml", go)
    write(studio / "samples" / "pre_shift_go.yaml", go)
    write(agents_root / "fixtures" / "hot_work_no_permit_abort.yaml", """zone_id: DEMO-L5-WELD
hot_work:
  required: true
  permit_valid: false
  no_permit: true
  combustibles_cleared: false
  extinguisher_staged: false
  active: true
fire_watch:
  required: true
  present_during: false
  post_watch_complete: false
ppe:
  missing: []
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "cse_gas_abort.yaml", """zone_id: DEMO-TANK-T2
cse:
  required: true
  permit_valid: false
  attendant_present: false
  gas_clear: false
  rescue_plan: false
ppe:
  missing: [respirator]
crew:
  roles: [safety_lead, supervisor, fire_watch, cse_attendant, competent_person, first_aid, qc_tech]
  briefing_complete: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "fall_unprotected_abort.yaml", """zone_id: DEMO-DECK-EDGE
fall:
  required: true
  unprotected: true
  harness_ok: false
  anchorage_ok: false
ppe:
  missing: [harness]
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "incident_stop_abort.yaml", """zone_id: DEMO-SITE-DAY
incident:
  stop_work: true
  serious_incident: true
  continuing: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "briefing_hold.yaml", """zone_id: DEMO-SITE-DAY
briefing:
  complete: false
  has_high_risk: true
  high_risk_called_out: false
ppe:
  missing: [fr_clothing]
impairment:
  fatigue_risk: true
weather:
  lightning: false
  high_wind: true
crew:
  roles: [safety_lead, supervisor, fire_watch, cse_attendant, competent_person, first_aid, qc_tech]
  briefing_complete: false
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")

    write(ROOT / "tests" / "test_daily_safety_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.daily_safety_swarm.swarm import DailySafetySwarm
from modules.daily_safety_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "daily-safety" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(DailySafetySwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_shift_go():
    assert DailySafetySwarm().run("pre-shift-safety-gate", _load("pre_shift_go.yaml")).decision == "GO"


def test_hot_work_no_permit_abort():
    assert DailySafetySwarm().run("hot-work-permit-gate", _load("hot_work_no_permit_abort.yaml")).decision == "ABORT"


def test_cse_gas_abort():
    assert DailySafetySwarm().run("confined-space-entry", _load("cse_gas_abort.yaml")).decision == "ABORT"


def test_fall_unprotected_abort():
    assert DailySafetySwarm().run("fall-protection-gate", _load("fall_unprotected_abort.yaml")).decision == "ABORT"


def test_incident_stop_abort():
    assert DailySafetySwarm().run("incident-abort", _load("incident_stop_abort.yaml")).decision == "ABORT"


def test_briefing_hold():
    assert DailySafetySwarm().run("pre-shift-safety-gate", _load("briefing_hold.yaml")).decision == "HOLD"


def test_hot_work_go():
    assert DailySafetySwarm().run("hot-work-permit-gate", _load("pre_shift_go.yaml")).decision == "GO"


def test_crane_go():
    assert DailySafetySwarm().run("crane-exclusion-gate", _load("pre_shift_go.yaml")).decision == "GO"


def test_hold_abort():
    assert DailySafetySwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "stop-work"}).decision == "ABORT"
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

### Daily Safety Swarm (Copilot Studio)

Same pattern — field GO/HOLD/ABORT for permits, hot work, CSE, LOTO, and fall protection:

- [`copilot-studio/daily-safety-crew/`](copilot-studio/daily-safety-crew/) — parent + 16 child agents; open `START_HERE.md`
- Drop-in zip: [`packages/DailySafety-Swarm-CopilotStudio-DropIn.zip`](packages/DailySafety-Swarm-CopilotStudio-DropIn.zip)

```bash
python -m modules.daily_safety_swarm.api --port 8095
python -m modules.daily_safety_swarm.cli run pre-shift-safety-gate -c agents/daily-safety/fixtures/pre_shift_go.yaml
```
"""
        if "Daily Safety Swarm" not in rtxt and marker in rtxt:
            readme.write_text(rtxt.replace(marker, block + "\n", 1))

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "DailySafety-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
