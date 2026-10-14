#!/usr/bin/env python3
"""Generate special inspections / SI hold-point coordinator swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("si-lead", "SiLead", "Owns SI program sequence and final GO/HOLD/ABORT.",
     """You own **special inspections (SI)** coordination across trades and assemble GO/HOLD/ABORT.

## Sequence pattern
1. Statement of Special Inspections (SOSSI) approved; agency hired
2. ITP / hold-point schedule aligned to pours, steel, soils, etc.
3. Credentials verified; inspectors dispatched before work
4. Trade SI performed; NCRs logged; no cover without release
5. NDT / lab results dispositioned
6. Final SI report package for AHJ / closeout

Do not invent code editions, inspector IDs, or test results."""),
    ("statement-of-si", "StatementOfSi", "Owns SOSSI scope and frequency matrix.",
     """You own the Statement of Special Inspections.

## Checks
- SOSSI approved by SER / AHJ as required
- Work items and continuous vs periodic frequency listed
- Deferred submittals / fabricator approvals noted

HOLD work starting without approved SOSSI for that scope."""),
    ("itp-scheduler", "ItpScheduler", "Owns hold-point calendar vs trade activities.",
     """You own SI scheduling.

## Checks
- Tomorrow's / today's hold points have named inspectors
- Notice lead time met (e.g. 24–48 hr)
- Conflicts resolved (same inspector double-booked)

HOLD trade start when required SI not scheduled."""),
    ("soils-foundation-si", "SoilsFoundationSi", "Owns soils, fill, and foundation SI hold points.",
     """You own soils/foundation special inspection.

## Checks
- Subgrade / fill density SI present when required
- Deep foundation tip/cleanout SI when in SOSSI
- Reports attached to area/element ID

HOLD fill/foundation cover without required soils SI."""),
    ("concrete-si", "ConcreteSi", "Owns rebar, prestress, and concrete placement SI.",
     """You own concrete special inspection.

## Checks
- Rebar/PT inspection before pour when continuous/periodic required
- Batch tickets / cylinders logged
- Cold/hot weather procedures observed when applicable

HOLD pour without required concrete SI present/sign-off."""),
    ("steel-si", "SteelSi", "Owns high-strength bolting, welding, and steel SI.",
     """You own structural steel special inspection.

## Checks
- Bolting/welding SI per SOSSI (RCSC / AWS)
- Fabricator approvals when required
- NDT hold points scheduled before paint/fireproofing

HOLD steel cover/fireproofing without required steel SI."""),
    ("masonry-si", "MasonrySi", "Owns masonry mortar, rebar, and grout SI.",
     """You own masonry special inspection.

## Checks
- Mortar/grout SI frequency met
- Pre-grout rebar SI when required
- Prism/grout specimens logged

HOLD grout/cover without required masonry SI."""),
    ("wood-si", "WoodSi", "Owns mass timber / wood framing SI when specified.",
     """You own wood/mass-timber special inspection.

## Checks
- Connection / fastener SI per SOSSI
- Moisture / grading observations when required
- Shop fabricator approvals

HOLD close-in without required wood SI."""),
    ("fire-resistance-si", "FireResistanceSi", "Owns SFRM / firestopping SI hold points.",
     """You own fire-resistance special inspection.

## Checks
- SFRM thickness/bond SI when required
- Through-penetration firestop SI / photo log
- Rated assembly continuity observations

HOLD concealment without required fire SI."""),
    ("ndt-testing", "NdtTesting", "Owns UT/MT/PT/RT and other NDT releases.",
     """You own nondestructive testing gates.

## Checks
- Required NDT procedures/techs qualified
- Indications dispositioned before cover
- Reports tied to weld/bolt IDs

HOLD paint/cover over open NDT."""),
    ("agency-credentials", "AgencyCredentials", "Owns SI agency and inspector qualifications.",
     """You own SI agency credentials.

## Checks
- Agency approved by AHJ / owner
- Inspector certifications current for the work type
- Independence / conflict rules observed

FAIL/HOLD if unapproved agency or expired credentials on a hold point."""),
    ("hold-point-release", "HoldPointRelease", "Owns signed release before cover/next trade.",
     """You own hold-point release.

## Checks
- Required SI sign-off recorded for the element
- No open critical NCRs on that element
- Cover/next trade authorized

FAIL if covering without SI release."""),
    ("nonconformance", "Nonconformance", "Owns SI NCR logging and disposition.",
     """You own SI nonconformances.

## Checks
- NCRs logged with element ID and photos
- SER / engineer disposition when required
- Rework verified before release

HOLD release with open critical NCRs."""),
    ("final-report", "FinalReport", "Owns final SI report package for AHJ/closeout.",
     """You own final SI reporting.

## Checks
- Daily reports compiled
- Final report signed by SI agency
- Outstanding items closed or listed

HOLD CO/turnover when final SI report required but missing."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work for skipped SI and unsafe access.",
     """You have stop-work authority. FAIL => swarm **ABORT**.

## Fail conditions
- Covering / concealing work before required SI release
- Unapproved SI agency performing hold points
- Critical structural hold point knowingly skipped
- Unsafe access denying inspector observation when required"""),
    ("crew-ops", "CrewOps", "Owns GC coordinator + SI agency staffing readiness.",
     """You own SI program staffing.

## Roles
si_lead, gc_coordinator, soils_inspector, concrete_inspector, steel_inspector, document_ctrl, safety_watch

HOLD missing roles for today's hold points or incomplete briefing."""),
]

WORKFLOWS = [
    "pre-si-program-gate",
    "daily-si-dispatch",
    "soils-foundation-hold",
    "concrete-pour-si-gate",
    "steel-connection-si-gate",
    "masonry-grout-si-gate",
    "fireproofing-si-gate",
    "ndt-release-gate",
    "cover-before-si-gate",
    "ncr-disposition-gate",
    "si-final-report",
    "hold-abort",
]

ROLES = (
    "si_lead",
    "gc_coordinator",
    "soils_inspector",
    "concrete_inspector",
    "steel_inspector",
    "document_ctrl",
    "safety_watch",
)

ORDERS = {
    "pre-si-program-gate": ["statement-of-si", "agency-credentials", "itp-scheduler", "crew-ops", "safety-failsafe", "qa-inspector"],
    "daily-si-dispatch": ["itp-scheduler", "agency-credentials", "crew-ops", "qa-inspector"],
    "soils-foundation-hold": ["soils-foundation-si", "hold-point-release", "nonconformance", "qa-inspector", "safety-failsafe"],
    "concrete-pour-si-gate": ["concrete-si", "hold-point-release", "agency-credentials", "qa-inspector", "safety-failsafe"],
    "steel-connection-si-gate": ["steel-si", "ndt-testing", "hold-point-release", "qa-inspector", "safety-failsafe"],
    "masonry-grout-si-gate": ["masonry-si", "hold-point-release", "qa-inspector", "safety-failsafe"],
    "fireproofing-si-gate": ["fire-resistance-si", "hold-point-release", "qa-inspector", "safety-failsafe"],
    "ndt-release-gate": ["ndt-testing", "steel-si", "nonconformance", "qa-inspector"],
    "cover-before-si-gate": ["hold-point-release", "nonconformance", "safety-failsafe", "qa-inspector"],
    "ncr-disposition-gate": ["nonconformance", "hold-point-release", "qa-inspector"],
    "si-final-report": ["final-report", "nonconformance", "statement-of-si", "agency-credentials", "crew-ops"],
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
    Decision: GO | HOLD | ABORT. Prefer SiContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: SiContextJson
    description: JSON context for special inspections hold points NCR cover
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    SiContextJson:
      displayName: SI Context JSON
      description: JSON context for special inspections
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
    agents_root = ROOT / "agents" / "special-inspections"
    studio = ROOT / "copilot-studio" / "special-inspections-crew"
    mod = ROOT / "modules" / "special_inspections_swarm"

    # qa-inspector is referenced in ORDERS but not in SPECIALISTS - add it
    specialists = list(SPECIALISTS)
    if not any(s[0] == "qa-inspector" for s in specialists):
        specialists.append(
            ("qa-inspector", "QaInspector", "Owns SI documentation completeness vs ITP.",
             """You own SI documentation QA.

## Checks
- Daily SI reports filed for completed hold points
- Photos / tickets attached
- Matrix of open hold points current

HOLD missing documentation for claimed releases.""")
        )

    write(agents_root / "SOURCES.md", """# Source basis for Special Inspections Swarm

From project `construction.md` extractions and typical IBC Chapter 17 SI practice:

- Statement of Special Inspections (SOSSI) + ITP hold-point coordination
- Soils, concrete, steel, masonry, wood, fire-resistance SI gates
- Cover-before-SI prohibition and final SI report for AHJ/closeout
""")
    write(agents_root / "README.md", """# Special Inspections Swarm (reference twin)

> See [`../../copilot-studio/special-inspections-crew/`](../../copilot-studio/special-inspections-crew/) → `START_HERE.md`.

```bash
python -m modules.special_inspections_swarm.cli list
python -m modules.special_inspections_swarm.cli run pre-si-program-gate -c agents/special-inspections/fixtures/pre_si_go.yaml
python -m modules.special_inspections_swarm.api --port 8093
```
""")

    for slug, folder, desc, instr in specialists:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# Special Inspections Swarm — Coordinator

Return one GO / HOLD / ABORT for SI hold-point coordination.

## Hard rules
1. No trade start without SOSSI + scheduled SI for that hold point.
2. Never cover/conceal work before SI release.
3. Credentials must be current for the work type.
4. Critical NCRs closed before release.
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

    children = ", ".join(s[1] for s in specialists)
    write(studio / "agent.mcs.yml", f"""mcs.metadata:
  componentName: SpecialInspectionsSwarm
kind: GptComponentMetadata
displayName: Special Inspections Swarm
instructions: |
  You are the Special Inspections / SI hold-point coordinator swarm.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect SiContextJson; missing critical fields => HOLD (do not invent readings).
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
  - title: Pre-SI program
    text: Run pre-si-program-gate — is SOSSI and agency ready?
  - title: Daily SI dispatch
    text: Run daily-si-dispatch for tomorrow's pours and steel.
  - title: Concrete pour SI
    text: Run concrete-pour-si-gate for Deck L4 pour.
  - title: Cover before SI
    text: Run cover-before-si-gate — can we fireproof yet?
  - title: NCR disposition
    text: Run ncr-disposition-gate for NCR-SI-18.
  - title: Final SI report
    text: Run si-final-report for AHJ package.

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: Special Inspections Swarm
schemaName: special_inspections_swarm
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
          - Special Inspections Swarm ready. Ask for pre-si-program-gate, daily-si-dispatch, concrete-pour-si-gate, cover-before-si-gate, ncr-disposition-gate, or another named workflow. I return GO / HOLD / ABORT.
          - SI online — share hold-point / trade context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.special_inspections_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nCross-cutting swarm for SI hold-point coordination.\n")
    write(studio / "START_HERE.md", """# START HERE — Special Inspections Swarm drop-in

Ready Copilot Studio workspace for SI / hold-point coordination.

## 3 steps
1. Open this `special-inspections-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Special Inspections Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-si-program-gate…”*.

## Workflows
`pre-si-program-gate`, `daily-si-dispatch`, `soils-foundation-hold`, `concrete-pour-si-gate`, `steel-connection-si-gate`, `masonry-grout-si-gate`, `fireproofing-si-gate`, `ndt-release-gate`, `cover-before-si-gate`, `ncr-disposition-gate`, `si-final-report`, `hold-abort`

## Optional backend
```bash
python -m modules.special_inspections_swarm.api --port 8093
python -m modules.special_inspections_swarm.cli run pre-si-program-gate -c agents/special-inspections/fixtures/pre_si_go.yaml
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

    # Truncate specialists count note: we have 17 with qa-inspector - that's fine (parent + children)
    # Actually masonry had 16. We now have 17 specialists. Fine.

    agents_src = r'''"""Deterministic specialist gates for special inspections."""

from __future__ import annotations

from typing import Any

from modules.special_inspections_swarm.schemas import GateResult

ERECT_ROLES = __ROLES__


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class StatementOfSiAgent:
    name = "statement-of-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("sossi") or {}
        if not s.get("approved"):
            return GateResult(self.name, "HOLD", "SOSSI not approved", {"sossi": s})
        if not s.get("frequency_matrix"):
            return GateResult(self.name, "HOLD", "SOSSI frequency matrix missing", {"sossi": s})
        return GateResult(self.name, "PASS", "SOSSI clear", {"sossi": s})


class ItpSchedulerAgent:
    name = "itp-scheduler"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        i = ctx.get("schedule") or {}
        if i.get("hold_points_staffed") is False:
            return GateResult(self.name, "HOLD", "Hold points not staffed: " + ", ".join(i.get("unstaffed") or ["unspecified"]), {"schedule": i})
        if i.get("notice_ok") is False:
            return GateResult(self.name, "HOLD", "SI notice lead time not met", {"schedule": i})
        return GateResult(self.name, "PASS", "SI schedule/dispatch clear", {"schedule": i})


class SoilsFoundationSiAgent:
    name = "soils-foundation-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("soils_si") or {}
        if s.get("required") is False:
            return GateResult(self.name, "SKIP", "No soils SI this gate", {})
        if not s.get("inspector_present") and s.get("required"):
            return GateResult(self.name, "HOLD", "Soils SI not present for hold point", {"soils_si": s})
        if s.get("accepted") is False:
            return GateResult(self.name, "HOLD", "Soils/foundation SI not accepted", {"soils_si": s})
        return GateResult(self.name, "PASS", "Soils/foundation SI clear", {"soils_si": s})


class ConcreteSiAgent:
    name = "concrete-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("concrete_si") or {}
        if c.get("required") is False:
            return GateResult(self.name, "SKIP", "No concrete SI this gate", {})
        if not c.get("inspector_present"):
            return GateResult(self.name, "HOLD", "Concrete SI not present for pour/rebar hold", {"concrete_si": c})
        if c.get("rebar_signed") is False:
            return GateResult(self.name, "HOLD", "Rebar/PT SI sign-off missing before pour", {"concrete_si": c})
        return GateResult(self.name, "PASS", "Concrete SI clear", {"concrete_si": c})


class SteelSiAgent:
    name = "steel-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("steel_si") or {}
        if s.get("required") is False:
            return GateResult(self.name, "SKIP", "No steel SI this gate", {})
        if not s.get("inspector_present"):
            return GateResult(self.name, "HOLD", "Steel SI not present", {"steel_si": s})
        if s.get("bolting_welding_ok") is False:
            return GateResult(self.name, "HOLD", "Bolting/welding SI incomplete", {"steel_si": s})
        return GateResult(self.name, "PASS", "Steel SI clear", {"steel_si": s})


class MasonrySiAgent:
    name = "masonry-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("masonry_si") or {}
        if m.get("required") is False:
            return GateResult(self.name, "SKIP", "No masonry SI this gate", {})
        if not m.get("inspector_present"):
            return GateResult(self.name, "HOLD", "Masonry SI not present", {"masonry_si": m})
        if m.get("pregrout_signed") is False:
            return GateResult(self.name, "HOLD", "Pre-grout SI sign-off missing", {"masonry_si": m})
        return GateResult(self.name, "PASS", "Masonry SI clear", {"masonry_si": m})


class WoodSiAgent:
    name = "wood-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("wood_si") or {}
        if w.get("required") is False:
            return GateResult(self.name, "SKIP", "No wood SI this gate", {})
        if not w.get("inspector_present"):
            return GateResult(self.name, "HOLD", "Wood/mass-timber SI not present", {"wood_si": w})
        return GateResult(self.name, "PASS", "Wood SI clear", {"wood_si": w})


class FireResistanceSiAgent:
    name = "fire-resistance-si"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("fire_si") or {}
        if f.get("required") is False:
            return GateResult(self.name, "SKIP", "No fire-resistance SI this gate", {})
        if not f.get("inspector_present"):
            return GateResult(self.name, "HOLD", "Fire-resistance SI not present", {"fire_si": f})
        if f.get("thickness_ok") is False:
            return GateResult(self.name, "HOLD", "SFRM/firestop SI thickness/continuity fail", {"fire_si": f})
        return GateResult(self.name, "PASS", "Fire-resistance SI clear", {"fire_si": f})


class NdtTestingAgent:
    name = "ndt-testing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        n = ctx.get("ndt") or {}
        if n.get("required") is False:
            return GateResult(self.name, "PASS", "NDT not required", {"ndt": n})
        if not n.get("complete"):
            return GateResult(self.name, "HOLD", "Required NDT incomplete", {"ndt": n})
        if n.get("open_indications"):
            return GateResult(self.name, "HOLD", "Open NDT indications: " + ", ".join(n["open_indications"]), {"ndt": n})
        return GateResult(self.name, "PASS", "NDT clear", {"ndt": n})


class AgencyCredentialsAgent:
    name = "agency-credentials"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("agency") or {}
        if a.get("approved") is False:
            return GateResult(self.name, "FAIL", "SI agency not approved by AHJ/owner", {"agency": a})
        if a.get("certs_current") is False:
            return GateResult(self.name, "HOLD", "Inspector certifications expired/missing for work type", {"agency": a})
        return GateResult(self.name, "PASS", "SI agency credentials clear", {"agency": a})


class HoldPointReleaseAgent:
    name = "hold-point-release"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        h = ctx.get("release") or {}
        if h.get("covering_without_si"):
            return GateResult(self.name, "FAIL", "Covering/concealing work without SI release", {"release": h})
        if not h.get("signed"):
            return GateResult(self.name, "HOLD", "Hold-point release not signed", {"release": h})
        if h.get("open_critical_ncrs"):
            return GateResult(self.name, "HOLD", "Critical NCRs open: " + ", ".join(h["open_critical_ncrs"]), {"release": h})
        return GateResult(self.name, "PASS", "Hold-point release clear", {"release": h})


class NonconformanceAgent:
    name = "nonconformance"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        n = ctx.get("ncr") or {}
        if n.get("required") is False and not n.get("open"):
            return GateResult(self.name, "PASS", "No open SI NCRs", {"ncr": n})
        if n.get("open"):
            critical = [x for x in n["open"] if x.get("critical")]
            if critical and not n.get("dispositioned"):
                return GateResult(self.name, "HOLD", "Critical SI NCRs not dispositioned", {"ncr": n})
            if n.get("rework_verified") is False:
                return GateResult(self.name, "HOLD", "SI NCR rework not verified", {"ncr": n})
        return GateResult(self.name, "PASS", "SI NCR status clear", {"ncr": n})


class FinalReportAgent:
    name = "final-report"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("final") or {}
        if not f.get("compiled"):
            return GateResult(self.name, "HOLD", "SI daily reports not compiled", {"final": f})
        if not f.get("agency_signed"):
            return GateResult(self.name, "HOLD", "Final SI report not signed by agency", {"final": f})
        if f.get("outstanding"):
            return GateResult(self.name, "HOLD", "Outstanding SI items: " + ", ".join(f["outstanding"]), {"final": f})
        return GateResult(self.name, "PASS", "Final SI report clear", {"final": f})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("release") or {}).get("covering_without_si"):
            violations.append("cover before required SI")
        if (ctx.get("agency") or {}).get("approved") is False:
            violations.append("unapproved SI agency on hold point")
        if (ctx.get("schedule") or {}).get("critical_skipped"):
            violations.append("critical structural hold point skipped")
        if (ctx.get("access") or {}).get("denied_unsafe"):
            violations.append("unsafe/denied access for required SI")
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
        if require_briefing and not crew.get("briefing_complete"):
            return GateResult(self.name, "HOLD", "SI coordination briefing incomplete", {})
        return GateResult(self.name, "PASS", f"SI staffing ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-SI program QA clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} SI docs clear", {})
        return GateResult(self.name, "HOLD", f"No SI QA evidence for phase={phase}", {"qa": q})


class SiLeadAgent:
    name = "si-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked SI / cover path"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"SI sequence ready for {ctx.get('zone_id', ctx.get('hold_point', 'hold'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named special inspections workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.special_inspections_swarm.agents import (
    AgencyCredentialsAgent,
    ConcreteSiAgent,
    CrewOpsAgent,
    FinalReportAgent,
    FireResistanceSiAgent,
    HoldPointReleaseAgent,
    ItpSchedulerAgent,
    MasonrySiAgent,
    NdtTestingAgent,
    NonconformanceAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SiLeadAgent,
    SoilsFoundationSiAgent,
    StatementOfSiAgent,
    SteelSiAgent,
)
from modules.special_inspections_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-si-program-gate",
    "daily-si-dispatch",
    "soils-foundation-hold",
    "concrete-pour-si-gate",
    "steel-connection-si-gate",
    "masonry-grout-si-gate",
    "fireproofing-si-gate",
    "ndt-release-gate",
    "cover-before-si-gate",
    "ncr-disposition-gate",
    "si-final-report",
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
        return ["Proceed to next SI / trade hold point", "File daily SI report + photos"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — do not cover; expose if already covered without SI",
            "Preserve hold-point IDs, photos, agency notes, timestamps",
            "Re-enter through pre-si-program-gate / cover-before-si-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "si-lead"]
    return [
        "Do not pour / cover / fireproof / grout until SI clears",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("hold_point") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.sossi = StatementOfSiAgent()
        self.schedule = ItpSchedulerAgent()
        self.soils = SoilsFoundationSiAgent()
        self.concrete = ConcreteSiAgent()
        self.steel = SteelSiAgent()
        self.masonry = MasonrySiAgent()
        self.fire = FireResistanceSiAgent()
        self.ndt = NdtTestingAgent()
        self.agency = AgencyCredentialsAgent()
        self.release = HoldPointReleaseAgent()
        self.ncr = NonconformanceAgent()
        self.final = FinalReportAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = SiLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_si_program_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.sossi.evaluate(ctx),
            self.agency.evaluate(ctx),
            self.schedule.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-si-program-gate", ctx, gates, {
            "GO": "SI program clear — hold points may be dispatched.",
            "HOLD": "SI program holding — SOSSI/agency/schedule.",
            "ABORT": "SI program aborted by fail-safe.",
        })

    def daily_si_dispatch(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.schedule.evaluate(ctx),
            self.agency.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("daily-si-dispatch", ctx, gates, {
            "GO": "Daily SI dispatch clear.",
            "HOLD": "Daily SI dispatch holding.",
            "ABORT": "Daily SI dispatch aborted.",
        })

    def soils_foundation_hold(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "soils_si": {**(ctx.get("soils_si") or {}), "required": True}}
        gates = [
            self.soils.evaluate(ctx),
            self.release.evaluate(ctx),
            self.ncr.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("soils-foundation-hold", ctx, gates, {
            "GO": "Soils/foundation SI hold clear.",
            "HOLD": "Soils/foundation SI holding.",
            "ABORT": "Soils/foundation SI aborted.",
        })

    def concrete_pour_si_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "concrete_si": {**(ctx.get("concrete_si") or {}), "required": True}}
        gates = [
            self.concrete.evaluate(ctx),
            self.release.evaluate(ctx),
            self.agency.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("concrete-pour-si-gate", ctx, gates, {
            "GO": "Concrete pour SI clear.",
            "HOLD": "Concrete pour SI holding.",
            "ABORT": "Concrete pour SI aborted.",
        })

    def steel_connection_si_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "steel_si": {**(ctx.get("steel_si") or {}), "required": True}}
        gates = [
            self.steel.evaluate(ctx),
            self.ndt.evaluate(ctx),
            self.release.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("steel-connection-si-gate", ctx, gates, {
            "GO": "Steel connection SI clear.",
            "HOLD": "Steel connection SI holding.",
            "ABORT": "Steel connection SI aborted.",
        })

    def masonry_grout_si_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "masonry_si": {**(ctx.get("masonry_si") or {}), "required": True}}
        gates = [
            self.masonry.evaluate(ctx),
            self.release.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("masonry-grout-si-gate", ctx, gates, {
            "GO": "Masonry grout SI clear.",
            "HOLD": "Masonry grout SI holding.",
            "ABORT": "Masonry grout SI aborted.",
        })

    def fireproofing_si_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "fire_si": {**(ctx.get("fire_si") or {}), "required": True}}
        gates = [
            self.fire.evaluate(ctx),
            self.release.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("fireproofing-si-gate", ctx, gates, {
            "GO": "Fireproofing SI clear.",
            "HOLD": "Fireproofing SI holding.",
            "ABORT": "Fireproofing SI aborted.",
        })

    def ndt_release_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.ndt.evaluate(ctx),
            self.steel.evaluate(ctx),
            self.ncr.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("ndt-release-gate", ctx, gates, {
            "GO": "NDT release clear.",
            "HOLD": "NDT release holding.",
            "ABORT": "NDT release aborted.",
        })

    def cover_before_si_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.release.evaluate(ctx),
            self.ncr.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("cover-before-si-gate", ctx, gates, {
            "GO": "Cover/next trade authorized after SI.",
            "HOLD": "Cover holding — SI release incomplete.",
            "ABORT": "Cover aborted — do not conceal.",
        })

    def ncr_disposition_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.ncr.evaluate(ctx),
            self.release.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("ncr-disposition-gate", ctx, gates, {
            "GO": "SI NCR disposition clear.",
            "HOLD": "SI NCR disposition holding.",
            "ABORT": "SI NCR disposition aborted.",
        })

    def si_final_report(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.final.evaluate(ctx),
            self.ncr.evaluate(ctx),
            self.sossi.evaluate(ctx),
            self.agency.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("si-final-report", ctx, gates, {
            "GO": "Final SI report clear.",
            "HOLD": "Final SI report holding.",
            "ABORT": "Final SI report aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "si-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "si_agency_pm")},
        )]
        summary = "ABORT escalated — stop work; do not cover." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
''')

    write(mod / "swarm.py", '''"""Special inspections swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.special_inspections_swarm.schemas import SwarmResult
from modules.special_inspections_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class SpecialInspectionsSwarm:
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
        log_event(f"[special-inspections-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[special-inspections-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["SpecialInspectionsSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.special_inspections_swarm.swarm import SpecialInspectionsSwarm, SwarmResult
from modules.special_inspections_swarm.workflows import WORKFLOW_IDS

__all__ = ["SpecialInspectionsSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for special inspections swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.special_inspections_swarm.swarm import SpecialInspectionsSwarm

app = typer.Typer(add_completion=False, help="Special inspections / SI hold-point swarm")


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
    for w in SpecialInspectionsSwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = SpecialInspectionsSwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "special-inspections" / "fixtures" / "pre_si_go.yaml"
    result = SpecialInspectionsSwarm().run("pre-si-program-gate", yaml.safe_load(fixture.read_text()))
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

from modules.special_inspections_swarm.swarm import SpecialInspectionsSwarm
from modules.special_inspections_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = SpecialInspectionsSwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[special-inspections-swarm-api] {self.address_string()} {fmt % args}")

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
        if isinstance(payload.get("SiContextJson"), str):
            try:
                context = {**context, **json.loads(payload["SiContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "SiContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8093)
    args = p.parse_args()
    print(f"Special inspections swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-SI-PROGRAM
hold_point: PROG-001
sossi:
  approved: true
  frequency_matrix: true
agency:
  approved: true
  certs_current: true
schedule:
  hold_points_staffed: true
  notice_ok: true
  unstaffed: []
  critical_skipped: false
soils_si:
  required: true
  inspector_present: true
  accepted: true
concrete_si:
  required: true
  inspector_present: true
  rebar_signed: true
steel_si:
  required: true
  inspector_present: true
  bolting_welding_ok: true
masonry_si:
  required: true
  inspector_present: true
  pregrout_signed: true
fire_si:
  required: true
  inspector_present: true
  thickness_ok: true
ndt:
  required: true
  complete: true
  open_indications: []
release:
  signed: true
  covering_without_si: false
  open_critical_ncrs: []
ncr:
  open: []
  dispositioned: true
  rework_verified: true
final:
  compiled: true
  agency_signed: true
  outstanding: []
crew:
  roles:
    - si_lead
    - gc_coordinator
    - soils_inspector
    - concrete_inspector
    - steel_inspector
    - document_ctrl
    - safety_watch
  headcount: 9
  briefing_complete: true
qa:
  pre_hold_points_clear: true
  install_hold_points_clear: true
access:
  denied_unsafe: false
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_si_go.yaml", go)
    write(studio / "samples" / "pre_si_go.yaml", go)
    write(agents_root / "fixtures" / "cover_without_si_abort.yaml", """zone_id: DEMO-DECK-L4
release:
  signed: false
  covering_without_si: true
  open_critical_ncrs: [NCR-SI-12]
ncr:
  open:
    - {id: NCR-SI-12, critical: true}
  dispositioned: false
  rework_verified: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "unapproved_agency_abort.yaml", """zone_id: DEMO-SI-PROGRAM
sossi:
  approved: true
  frequency_matrix: true
agency:
  approved: false
  certs_current: false
schedule:
  hold_points_staffed: true
  notice_ok: true
crew:
  roles: [si_lead, gc_coordinator, soils_inspector, concrete_inspector, steel_inspector, document_ctrl, safety_watch]
  briefing_complete: true
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "pour_no_inspector_hold.yaml", """zone_id: DEMO-DECK-L4
concrete_si:
  required: true
  inspector_present: false
  rebar_signed: false
agency:
  approved: true
  certs_current: true
release:
  signed: false
  covering_without_si: false
  open_critical_ncrs: []
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "ndt_open_hold.yaml", """zone_id: DEMO-STEEL-GRID-B
ndt:
  required: true
  complete: false
  open_indications: [Weld-B12-UT]
steel_si:
  required: true
  inspector_present: true
  bolting_welding_ok: false
ncr:
  open:
    - {id: NCR-SI-22, critical: true}
  dispositioned: false
  rework_verified: false
qa:
  install_hold_points_clear: true
""")
    write(agents_root / "fixtures" / "sossi_missing_hold.yaml", """zone_id: DEMO-SI-PROGRAM
sossi:
  approved: false
  frequency_matrix: false
agency:
  approved: true
  certs_current: true
schedule:
  hold_points_staffed: false
  notice_ok: false
  unstaffed: [concrete_pour_L4, steel_bolt_B]
crew:
  roles: [si_lead, gc_coordinator, soils_inspector, concrete_inspector, steel_inspector, document_ctrl, safety_watch]
  briefing_complete: false
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")

    write(ROOT / "tests" / "test_special_inspections_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.special_inspections_swarm.swarm import SpecialInspectionsSwarm
from modules.special_inspections_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "special-inspections" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(SpecialInspectionsSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_si_go():
    assert SpecialInspectionsSwarm().run("pre-si-program-gate", _load("pre_si_go.yaml")).decision == "GO"


def test_cover_without_si_abort():
    assert SpecialInspectionsSwarm().run("cover-before-si-gate", _load("cover_without_si_abort.yaml")).decision == "ABORT"


def test_unapproved_agency_abort():
    assert SpecialInspectionsSwarm().run("pre-si-program-gate", _load("unapproved_agency_abort.yaml")).decision == "ABORT"


def test_pour_no_inspector_hold():
    assert SpecialInspectionsSwarm().run("concrete-pour-si-gate", _load("pour_no_inspector_hold.yaml")).decision == "HOLD"


def test_ndt_open_hold():
    assert SpecialInspectionsSwarm().run("ndt-release-gate", _load("ndt_open_hold.yaml")).decision == "HOLD"


def test_sossi_missing_hold():
    assert SpecialInspectionsSwarm().run("pre-si-program-gate", _load("sossi_missing_hold.yaml")).decision == "HOLD"


def test_concrete_go():
    assert SpecialInspectionsSwarm().run("concrete-pour-si-gate", _load("pre_si_go.yaml")).decision == "GO"


def test_final_report_go():
    assert SpecialInspectionsSwarm().run("si-final-report", _load("pre_si_go.yaml")).decision == "GO"


def test_hold_abort():
    assert SpecialInspectionsSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "cover"}).decision == "ABORT"
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

### Special Inspections Swarm (Copilot Studio)

Same pattern — cross-cutting GO/HOLD/ABORT for SI hold-point coordination:

- [`copilot-studio/special-inspections-crew/`](copilot-studio/special-inspections-crew/) — parent + specialists; open `START_HERE.md`
- Drop-in zip: [`packages/SpecialInspections-Swarm-CopilotStudio-DropIn.zip`](packages/SpecialInspections-Swarm-CopilotStudio-DropIn.zip)

```bash
python -m modules.special_inspections_swarm.api --port 8093
python -m modules.special_inspections_swarm.cli run pre-si-program-gate -c agents/special-inspections/fixtures/pre_si_go.yaml
```
"""
        if "Special Inspections Swarm" not in rtxt and marker in rtxt:
            readme.write_text(rtxt.replace(marker, block + "\n", 1))

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "SpecialInspections-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
