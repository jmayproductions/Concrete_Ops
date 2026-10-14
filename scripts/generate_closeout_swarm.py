#!/usr/bin/env python3
"""Generate closeout / punch / turnover field swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("closeout-lead", "CloseoutLead", "Owns closeout sequence and final GO/HOLD/ABORT.",
     """You own **punchlist / closeout / turnover** sequencing and assemble GO/HOLD/ABORT.

## Sequence pattern
1. Room readiness + finishes walkable
2. Punchlist generated trade-by-trade with owners + due dates
3. Life safety / door hardware / egress clear for TCO path
4. Fire protection / Cx / TAB sign-offs as required
5. NCR closeout + re-inspections complete
6. As-builts, O&M, warranties assembled
7. Digital turnover package + signature chain before client handoff

Do not invent inspection results or signature status."""),
    ("room-readiness", "RoomReadiness", "Owns room readiness before punch walks.",
     """You own room readiness.

## Checks
- Ceilings complete; lights/HVAC operating as required for walk
- Labels/controls visible
- Safe access for inspectors
- Major incomplete scopes flagged (not walkable)

HOLD rooms not ready for punch walk."""),
    ("punchlist", "Punchlist", "Owns deficiency logging, owners, and reinspect dates.",
     """You own punchlist workflow.

## Checks
- Trade-by-trade walk complete for zone
- Deficiencies photo-logged with location
- Responsible party + target close date assigned
- Re-inspection scheduled for closed items
- Open critical punches block TCO/turnover

HOLD missing owners or unlogged critical deficiencies."""),
    ("life-safety", "LifeSafety", "Owns egress, exit signs, and life-safety readiness.",
     """You own life-safety / egress QA for closeout.

## Checks
- Clear egress paths (min width per project/IBC class)
- Exit signs illuminated / correct arrows
- Door swings / stair geometry per code where applicable
- Emergency lighting tested under backup power when required

HOLD blocked egress or failed emergency lighting."""),
    ("door-hardware", "DoorHardware", "Owns door schedule match, fire labels, and function tests.",
     """You own door/hardware closeout QA.

## Checks
- Door ID matches schedule (type, rating, hardware group)
- Closers, latches, panic hardware function
- Fire-rated doors: label visible, seals, gap tolerances
- ADA opening force when specified

HOLD mismatched hardware or missing fire labels."""),
    ("finishes-qa", "FinishesQa", "Owns paint, flooring, ceilings, and finish punch.",
     """You own finish QA at closeout.

## Checks
- Paint coverage/evenness per project
- Flooring substrate/install defects logged
- Ceiling grids/tiles seated; fixtures aligned
- Caulk/trim deficiencies assigned

HOLD systemic finish failures without rework plan."""),
    ("fire-protection", "FireProtection", "Owns sprinkler, alarm, standpipe, damper closeout tests.",
     """You own fire protection closeout evidence.

## Checks
- Sprinkler hydro / alarm functional / standpipe / damper tests per project (NFPA class)
- Open failed tests block TCO
- Devices tagged and accessible

HOLD missing required FP test reports."""),
    ("commissioning", "Commissioning", "Owns CxA/TAB sign-off and prefunctional checklists.",
     """You own commissioning / TAB closeout.

## Checks
- Prefunctional checklists complete for systems in scope
- TAB report signed when required
- CxA sign-off / issues log closed or accepted
- Trend logs / calibration certs attached when required

HOLD missing Cx/TAB for systems claiming turnover."""),
    ("ncr-closeout", "NcrCloseout", "Owns NCR resolution and reinspection evidence.",
     """You own NCR closeout.

## Checks
- Open NCRs inventoried
- High-risk NCRs closed with reinspect
- Late/open high-risk NCRs block turnover
- Affidavits / corrective evidence attached

HOLD open high-risk NCRs."""),
    ("asbuilts-om", "AsbuiltsOm", "Owns as-builts, O&M manuals, and warranty logs.",
     """You own documentation turnover content.

## Checks
- As-built drawings current (redlines incorporated)
- O&M manuals complete for equipment in scope
- Warranty log by system/manufacturer
- Material certifications packaged

HOLD missing critical as-builts/O&Ms for handoff."""),
    ("turnover-package", "TurnoverPackage", "Owns digital handoff binder and archive completeness.",
     """You own the turnover package assembly.

## Package typically includes
- Master inspection log
- NCR closeout summary
- Certs + photos of corrections
- Digital signatures / role verification
- Subcontractor compliance affidavits

HOLD incomplete package before client portal release."""),
    ("signature-chain", "SignatureChain", "Owns approval signatures and role verification.",
     """You own signature / approval chain.

## Checks
- Required roles signed (QA, PM, CxA, etc. per project)
- Timestamps / document IDs recorded
- Rejected items returned with owner
- Legal archive trigger only after chain complete

HOLD missing required signatures."""),
    ("ahj-tco", "AhjTco", "Owns AHJ inspection prep and TCO readiness.",
     """You own AHJ / TCO readiness.

## Checks
- AHJ checklist items complete or tracked
- Mock walk with superintendent/PM done
- Open RFIs affecting occupancy resolved or accepted
- Life safety + FP evidence ready for inspector

HOLD TCO walk if critical life-safety open."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work / no-occupy authority for unsafe closeout conditions.",
     """Stop-occupy / stop-handoff authority.

## Immediate ABORT
- Occupancy attempted with blocked egress / failed life safety
- Client handoff with open high-risk life-safety NCR
- Forged/missing critical life-safety sign-offs

SafetyFailsafe FAIL => parent Decision ABORT."""),
    ("crew-ops", "CrewOps", "Owns closeout walk roles and briefing.",
     """You own closeout walk crew readiness.

## Typical roles
closeout_lead, qa_lead, pm_rep, trade_rep, cx_rep (if Cx), safety_watch

HOLD missing walk roles for scheduled punch/TCO."""),
    ("qa-inspector", "QaInspector", "Owns closeout hold points, photo evidence, and audit trail.",
     """You own closeout QC evidence.

## Evidence
- Punch photos + locations
- Reinspect pass records
- Archive PDF/JSON trail when required
- Missing phase evidence => HOLD
"""),
]

WORKFLOWS = [
    "pre-closeout-gate",
    "room-readiness-gate",
    "punchlist-walk",
    "life-safety-gate",
    "door-hardware-qa",
    "finishes-punch-gate",
    "fire-protection-closeout",
    "commissioning-gate",
    "ncr-closeout-gate",
    "tco-readiness-gate",
    "turnover-package-gate",
    "hold-abort",
]

ROLES = (
    "closeout_lead",
    "qa_lead",
    "pm_rep",
    "trade_rep",
    "safety_watch",
)

ORDERS = {
    "pre-closeout-gate": ["room-readiness", "punchlist", "crew-ops", "safety-failsafe", "qa-inspector"],
    "room-readiness-gate": ["room-readiness", "finishes-qa", "qa-inspector"],
    "punchlist-walk": ["punchlist", "room-readiness", "qa-inspector", "crew-ops"],
    "life-safety-gate": ["life-safety", "door-hardware", "fire-protection", "safety-failsafe", "qa-inspector"],
    "door-hardware-qa": ["door-hardware", "life-safety", "qa-inspector"],
    "finishes-punch-gate": ["finishes-qa", "punchlist", "qa-inspector"],
    "fire-protection-closeout": ["fire-protection", "commissioning", "qa-inspector", "safety-failsafe"],
    "commissioning-gate": ["commissioning", "asbuilts-om", "qa-inspector"],
    "ncr-closeout-gate": ["ncr-closeout", "punchlist", "qa-inspector", "safety-failsafe"],
    "tco-readiness-gate": ["ahj-tco", "life-safety", "fire-protection", "ncr-closeout", "signature-chain", "safety-failsafe", "qa-inspector"],
    "turnover-package-gate": ["turnover-package", "asbuilts-om", "signature-chain", "ncr-closeout", "commissioning", "qa-inspector", "crew-ops"],
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
    Decision: GO | HOLD | ABORT. Prefer CloseoutContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: CloseoutContextJson
    description: JSON context for punch TCO turnover docs signatures
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    CloseoutContextJson:
      displayName: Closeout Context JSON
      description: JSON context for closeout / punch / turnover
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
    agents_root = ROOT / "agents" / "closeout"
    studio = ROOT / "copilot-studio" / "closeout-crew"
    mod = ROOT / "modules" / "closeout_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for Closeout / Punch / Turnover Swarm

From project `construction.md` extractions:

- Pre-Closeout Workflow (room readiness, finishes, binder, Cx report)
- QAQC Documentation + Closeout (punchlist closeout checklist + reporting flow)
- Turnover Package System (inspection log, NCR summary, certs, signatures)
- Life Safety + Door Hardware QA + Punchlist Closeout / TCO readiness
""")
    write(agents_root / "README.md", """# Closeout / Punch / Turnover Swarm (reference twin)

> See [`../../copilot-studio/closeout-crew/`](../../copilot-studio/closeout-crew/) → `START_HERE.md`.

```bash
python -m modules.closeout_swarm.cli list
python -m modules.closeout_swarm.cli run pre-closeout-gate -c agents/closeout/fixtures/pre_closeout_go.yaml
python -m modules.closeout_swarm.api --port 8087
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# Closeout / Punch / Turnover Swarm — Coordinator

Return one GO / HOLD / ABORT for punch, TCO, and digital turnover.

## Hard rules
1. No TCO with open life-safety / fire-protection failures.
2. Every punch item needs owner + due date + photo evidence.
3. High-risk NCRs must be closed with reinspect before handoff.
4. Turnover package incomplete => HOLD (not client release).
5. SafetyFailsafe FAIL => ABORT (no occupy / no handoff).
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
  componentName: CloseoutTurnoverSwarm
kind: GptComponentMetadata
displayName: Closeout Turnover Swarm
instructions: |
  You are the Closeout / Punch / Turnover Swarm coordinator for room readiness,
  punchlist, life safety, commissioning, NCR closeout, TCO, and digital handoff.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect CloseoutContextJson; missing critical fields => HOLD (do not invent readings).
  3. Invoke child agents IN DOCUMENTED ORDER for that workflow.
  4. Wait for Decision/Summary/GatesJson/ActionsJson from each child.
  5. One parent reply only. Children must not reply to the field user.
  6. SafetyFailsafe FAIL => final Decision ABORT (no occupy / no handoff).

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
  - title: Pre-closeout
    text: Run pre-closeout-gate for Level 3 and return GO/HOLD/ABORT.
  - title: Punch walk
    text: Run punchlist-walk for Area B — owners and due dates assigned?
  - title: Life safety
    text: Run life-safety-gate before the AHJ walk.
  - title: TCO readiness
    text: Run tco-readiness-gate — are we clear for temporary occupancy?
  - title: NCR closeout
    text: Run ncr-closeout-gate for open high-risk items.
  - title: Turnover package
    text: Run turnover-package-gate before client portal release.

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: Closeout Turnover Swarm
schemaName: closeout_turnoverSwarm
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
          - Closeout Turnover Swarm ready. Ask for pre-closeout-gate, punchlist-walk, life-safety-gate, tco-readiness-gate, turnover-package-gate, or another named workflow. I return GO / HOLD / ABORT.
          - Closeout online — share zone/floor context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.closeout_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for punchlist, TCO, and digital turnover.\n")
    write(studio / "START_HERE.md", """# START HERE — Closeout Turnover Swarm drop-in

Ready Copilot Studio workspace for punch / TCO / turnover gates.

## 3 steps
1. Open this `closeout-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Closeout Turnover Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-closeout-gate…”*.

## Workflows
`pre-closeout-gate`, `room-readiness-gate`, `punchlist-walk`, `life-safety-gate`, `door-hardware-qa`, `finishes-punch-gate`, `fire-protection-closeout`, `commissioning-gate`, `ncr-closeout-gate`, `tco-readiness-gate`, `turnover-package-gate`, `hold-abort`

## Optional backend
```bash
python -m modules.closeout_swarm.api --port 8087
python -m modules.closeout_swarm.cli run pre-closeout-gate -c agents/closeout/fixtures/pre_closeout_go.yaml
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

    agents_src = r'''"""Deterministic specialist gates for closeout / punch / turnover."""

from __future__ import annotations

from typing import Any

from modules.closeout_swarm.schemas import GateResult

ERECT_ROLES = __ROLES__


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


class RoomReadinessAgent:
    name = "room-readiness"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        r = ctx.get("rooms") or {}
        if r.get("walkable") is False:
            return GateResult(self.name, "HOLD", "Rooms not walkable for punch: " + ", ".join(r.get("blocked_rooms") or ["see list"]), {"rooms": r})
        miss = _missing(r, ("ceilings_complete", "systems_operating", "safe_access"))
        if miss:
            return GateResult(self.name, "HOLD", "Room readiness incomplete: " + ", ".join(miss), {"rooms": r})
        return GateResult(self.name, "PASS", "Room readiness clear", {"rooms": r})


class PunchlistAgent:
    name = "punchlist"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("punch") or {}
        if not p.get("walk_complete"):
            return GateResult(self.name, "HOLD", "Punch walk not complete for zone", {"punch": p})
        if p.get("items_without_owner"):
            return GateResult(self.name, "HOLD", "Punch items missing owners: " + ", ".join(p["items_without_owner"][:8]), {"punch": p})
        open_critical = list(p.get("open_critical") or [])
        if open_critical and ctx.get("require_critical_clear"):
            return GateResult(self.name, "HOLD", "Open critical punches: " + ", ".join(open_critical[:8]), {"punch": p})
        if not p.get("photos_logged"):
            return GateResult(self.name, "HOLD", "Punch photo log incomplete", {"punch": p})
        return GateResult(self.name, "PASS", "Punchlist process clear", {"punch": p})


class LifeSafetyAgent:
    name = "life-safety"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("life_safety") or {}
        miss = _missing(l, ("egress_clear", "exit_signs_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Life safety incomplete: " + ", ".join(miss), {"life_safety": l})
        if l.get("emergency_lighting_failed"):
            return GateResult(self.name, "FAIL", "Emergency lighting failed under backup power", {"life_safety": l})
        if l.get("egress_blocked"):
            return GateResult(self.name, "FAIL", "Egress path blocked", {"life_safety": l})
        return GateResult(self.name, "PASS", "Life safety clear", {"life_safety": l})


class DoorHardwareAgent:
    name = "door-hardware"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("doors") or {}
        if not d and not ctx.get("require_doors"):
            return GateResult(self.name, "SKIP", "No door scope", {})
        if d.get("schedule_mismatches"):
            return GateResult(self.name, "HOLD", "Door/hardware mismatches: " + ", ".join(d["schedule_mismatches"][:8]), {"doors": d})
        if d.get("missing_fire_labels"):
            return GateResult(self.name, "HOLD", "Missing fire door labels: " + ", ".join(d["missing_fire_labels"][:8]), {"doors": d})
        if not d.get("function_tested"):
            return GateResult(self.name, "HOLD", "Door function tests incomplete", {"doors": d})
        return GateResult(self.name, "PASS", "Door/hardware clear", {"doors": d})


class FinishesQaAgent:
    name = "finishes-qa"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("finishes") or {}
        if f.get("systemic_failures"):
            return GateResult(self.name, "HOLD", "Systemic finish failures without rework plan", {"finishes": f})
        if not f.get("walk_complete") and ctx.get("require_finishes"):
            return GateResult(self.name, "HOLD", "Finishes punch walk incomplete", {"finishes": f})
        return GateResult(self.name, "PASS", "Finishes QA clear", {"finishes": f})


class FireProtectionAgent:
    name = "fire-protection"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        fp = ctx.get("fire_protection") or {}
        if fp.get("required") is False:
            return GateResult(self.name, "PASS", "FP closeout not required this gate", {"fire_protection": fp})
        if not fp.get("tests_complete"):
            return GateResult(self.name, "HOLD", "Required fire protection tests incomplete", {"fire_protection": fp})
        if fp.get("tests_failed"):
            return GateResult(self.name, "FAIL", "Fire protection tests failed: " + ", ".join(fp["tests_failed"]), {"fire_protection": fp})
        return GateResult(self.name, "PASS", "Fire protection closeout clear", {"fire_protection": fp})


class CommissioningAgent:
    name = "commissioning"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("commissioning") or {}
        if c.get("required") is False:
            return GateResult(self.name, "PASS", "Cx/TAB not required this gate", {"commissioning": c})
        miss = _missing(c, ("prefunctional_complete", "tab_signed", "cxa_signed"))
        if miss:
            return GateResult(self.name, "HOLD", "Commissioning incomplete: " + ", ".join(miss), {"commissioning": c})
        return GateResult(self.name, "PASS", "Commissioning/TAB clear", {"commissioning": c})


class NcrCloseoutAgent:
    name = "ncr-closeout"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        n = ctx.get("ncr") or {}
        open_high = list(n.get("open_high_risk") or [])
        if open_high:
            return GateResult(self.name, "HOLD", "Open high-risk NCRs: " + ", ".join(open_high[:8]), {"ncr": n})
        if n.get("reinspect_pending"):
            return GateResult(self.name, "HOLD", "NCR reinspection pending", {"ncr": n})
        return GateResult(self.name, "PASS", "NCR closeout clear", {"ncr": n})


class AsbuiltsOmAgent:
    name = "asbuilts-om"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("docs") or {}
        miss = _missing(a, ("asbuilts_current", "om_complete", "warranty_log"))
        if miss:
            return GateResult(self.name, "HOLD", "Docs incomplete: " + ", ".join(miss), {"docs": a})
        return GateResult(self.name, "PASS", "As-builts/O&M/warranties clear", {"docs": a})


class TurnoverPackageAgent:
    name = "turnover-package"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("turnover") or {}
        miss = _missing(t, ("inspection_log", "ncr_summary", "certs_packaged", "photos_packaged"))
        if miss:
            return GateResult(self.name, "HOLD", "Turnover package incomplete: " + ", ".join(miss), {"turnover": t})
        return GateResult(self.name, "PASS", "Turnover package assembled", {"turnover": t})


class SignatureChainAgent:
    name = "signature-chain"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("signatures") or {}
        missing = list(s.get("missing_roles") or [])
        if missing:
            return GateResult(self.name, "HOLD", "Missing signatures: " + ", ".join(missing), {"signatures": s})
        if not s.get("chain_complete"):
            return GateResult(self.name, "HOLD", "Signature chain incomplete", {"signatures": s})
        return GateResult(self.name, "PASS", "Signature chain complete", {"signatures": s})


class AhjTcoAgent:
    name = "ahj-tco"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("tco") or {}
        if not a.get("mock_walk_complete"):
            return GateResult(self.name, "HOLD", "Mock TCO/AHJ walk not complete", {"tco": a})
        if a.get("open_occupancy_rfis"):
            return GateResult(self.name, "HOLD", "Open occupancy RFIs: " + ", ".join(a["open_occupancy_rfis"][:8]), {"tco": a})
        if not a.get("binder_ready"):
            return GateResult(self.name, "HOLD", "TCO binder/evidence not ready", {"tco": a})
        return GateResult(self.name, "PASS", "TCO/AHJ readiness clear", {"tco": a})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("life_safety", {}).get("egress_blocked"):
            violations.append("blocked egress")
        if ctx.get("life_safety", {}).get("emergency_lighting_failed"):
            violations.append("failed emergency lighting")
        if ctx.get("handoff", {}).get("attempted_with_life_safety_ncr"):
            violations.append("handoff with open life-safety NCR")
        if violations:
            return GateResult(self.name, "FAIL", "STOP-OCCUPY/HANDOFF: " + "; ".join(violations), {"violations": violations})
        return GateResult(self.name, "PASS", "No fail-safe violations", {})


class CrewOpsAgent:
    name = "crew-ops"

    def evaluate(self, ctx: dict[str, Any], require_briefing: bool = True) -> GateResult:
        crew = ctx.get("crew") or {}
        roles = set(crew.get("roles") or [])
        required = list(ERECT_ROLES)
        if (ctx.get("commissioning") or {}).get("required"):
            if "cx_rep" not in roles:
                required.append("cx_rep")
        missing = [r for r in required if r not in roles]
        if missing:
            return GateResult(self.name, "HOLD", "Missing roles: " + ", ".join(missing), {"missing": missing})
        if require_briefing and not crew.get("briefing_complete"):
            return GateResult(self.name, "HOLD", "Closeout walk briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Crew ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-closeout QA hold points clear", {})
        if phase != "pre" and q.get("closeout_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class CloseoutLeadAgent:
    name = "closeout-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked occupy/handoff"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named closeout / punch / turnover workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.closeout_swarm.agents import (
    AhjTcoAgent,
    AsbuiltsOmAgent,
    CloseoutLeadAgent,
    CommissioningAgent,
    CrewOpsAgent,
    DoorHardwareAgent,
    FinishesQaAgent,
    FireProtectionAgent,
    LifeSafetyAgent,
    NcrCloseoutAgent,
    PunchlistAgent,
    QaInspectorAgent,
    RoomReadinessAgent,
    SafetyFailsafeAgent,
    SignatureChainAgent,
    TurnoverPackageAgent,
)
from modules.closeout_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-closeout-gate",
    "room-readiness-gate",
    "punchlist-walk",
    "life-safety-gate",
    "door-hardware-qa",
    "finishes-punch-gate",
    "fire-protection-closeout",
    "commissioning-gate",
    "ncr-closeout-gate",
    "tco-readiness-gate",
    "turnover-package-gate",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status == "FAIL" and g.agent != "closeout-lead" for g in active):
        # life-safety/FP FAIL promotes via safety agent typically; otherwise HOLD
        return "HOLD"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next closeout sequence / workflow", "Keep punch tracker + archive current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "NO OCCUPY / NO HANDOFF — secure life-safety issues",
            "Preserve photos, test reports, punch/NCR logs, signatures",
            "Re-enter through pre-closeout-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "closeout-lead"]
    return [
        "Do not release TCO or client turnover",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.rooms = RoomReadinessAgent()
        self.punch = PunchlistAgent()
        self.life = LifeSafetyAgent()
        self.doors = DoorHardwareAgent()
        self.finishes = FinishesQaAgent()
        self.fp = FireProtectionAgent()
        self.cx = CommissioningAgent()
        self.ncr = NcrCloseoutAgent()
        self.docs = AsbuiltsOmAgent()
        self.turnover = TurnoverPackageAgent()
        self.sigs = SignatureChainAgent()
        self.tco = AhjTcoAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = CloseoutLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        # Promote life-safety/FP FAIL into safety abort when occupy/handoff workflows
        if workflow in {"life-safety-gate", "tco-readiness-gate", "turnover-package-gate"}:
            for g in list(gates):
                if g.status == "FAIL" and g.agent in {"life-safety", "fire-protection"}:
                    if not any(x.agent == "safety-failsafe" and x.status == "FAIL" for x in gates):
                        gates.append(GateResult("safety-failsafe", "FAIL", g.detail, g.evidence))
                    break
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_closeout_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.rooms.evaluate(ctx),
            self.punch.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-closeout-gate", ctx, gates, {
            "GO": "Pre-closeout clear — punch/TCO sequence may proceed.",
            "HOLD": "Pre-closeout holding — rooms/punch/crew.",
            "ABORT": "Pre-closeout aborted by fail-safe.",
        })

    def room_readiness_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.rooms.evaluate(ctx), self.finishes.evaluate(ctx), self.qa.evaluate(ctx, phase="pre")]
        return self._finish("room-readiness-gate", ctx, gates, {
            "GO": "Room readiness clear.",
            "HOLD": "Room readiness holding.",
            "ABORT": "Room readiness aborted.",
        })

    def punchlist_walk(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.punch.evaluate(ctx),
            self.rooms.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("punchlist-walk", ctx, gates, {
            "GO": "Punchlist walk clear.",
            "HOLD": "Punchlist holding.",
            "ABORT": "Punchlist aborted.",
        })

    def life_safety_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.life.evaluate(ctx),
            self.doors.evaluate({**ctx, "require_doors": True}),
            self.fp.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("life-safety-gate", ctx, gates, {
            "GO": "Life safety clear.",
            "HOLD": "Life safety holding.",
            "ABORT": "Life safety aborted — no occupy.",
        })

    def door_hardware_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.doors.evaluate({**ctx, "require_doors": True}),
            self.life.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("door-hardware-qa", ctx, gates, {
            "GO": "Door/hardware QA clear.",
            "HOLD": "Door/hardware holding.",
            "ABORT": "Door/hardware aborted.",
        })

    def finishes_punch_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.finishes.evaluate({**ctx, "require_finishes": True}),
            self.punch.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("finishes-punch-gate", ctx, gates, {
            "GO": "Finishes punch clear.",
            "HOLD": "Finishes holding.",
            "ABORT": "Finishes aborted.",
        })

    def fire_protection_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.fp.evaluate(ctx),
            self.cx.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("fire-protection-closeout", ctx, gates, {
            "GO": "Fire protection closeout clear.",
            "HOLD": "Fire protection holding.",
            "ABORT": "Fire protection aborted.",
        })

    def commissioning_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.cx.evaluate({**ctx, "commissioning": {**(ctx.get("commissioning") or {}), "required": True}}),
            self.docs.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
        ]
        return self._finish("commissioning-gate", ctx, gates, {
            "GO": "Commissioning/TAB clear.",
            "HOLD": "Commissioning holding.",
            "ABORT": "Commissioning aborted.",
        })

    def ncr_closeout_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.ncr.evaluate(ctx),
            self.punch.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("ncr-closeout-gate", ctx, gates, {
            "GO": "NCR closeout clear.",
            "HOLD": "NCR closeout holding.",
            "ABORT": "NCR closeout aborted.",
        })

    def tco_readiness_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.tco.evaluate(ctx),
            self.life.evaluate(ctx),
            self.fp.evaluate(ctx),
            self.ncr.evaluate(ctx),
            self.sigs.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
        ]
        return self._finish("tco-readiness-gate", ctx, gates, {
            "GO": "TCO readiness clear.",
            "HOLD": "TCO holding.",
            "ABORT": "TCO aborted — no occupy.",
        })

    def turnover_package_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.turnover.evaluate(ctx),
            self.docs.evaluate(ctx),
            self.sigs.evaluate(ctx),
            self.ncr.evaluate(ctx),
            self.cx.evaluate(ctx),
            self.qa.evaluate(ctx, phase="post"),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("turnover-package-gate", ctx, gates, {
            "GO": "Turnover package clear for client handoff.",
            "HOLD": "Turnover package holding.",
            "ABORT": "Turnover aborted — no handoff.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        reason = ctx.get("block_reason") or "unspecified gate failure"
        severity = (ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        gates = [GateResult(
            "safety-failsafe" if decision == "ABORT" else "closeout-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "project_manager")},
        )]
        summary = "ABORT escalated — no occupy/handoff." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
''')

    write(mod / "swarm.py", '''"""Closeout / punch / turnover swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.closeout_swarm.schemas import SwarmResult
from modules.closeout_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class CloseoutSwarm:
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
        log_event(f"[closeout-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[closeout-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["CloseoutSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.closeout_swarm.swarm import CloseoutSwarm, SwarmResult
from modules.closeout_swarm.workflows import WORKFLOW_IDS

__all__ = ["CloseoutSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for closeout / punch / turnover swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.closeout_swarm.swarm import CloseoutSwarm

app = typer.Typer(add_completion=False, help="Closeout / punch / turnover swarm")


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
    for w in CloseoutSwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = CloseoutSwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "closeout" / "fixtures" / "pre_closeout_go.yaml"
    result = CloseoutSwarm().run("pre-closeout-gate", yaml.safe_load(fixture.read_text()))
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

from modules.closeout_swarm.swarm import CloseoutSwarm
from modules.closeout_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = CloseoutSwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[closeout-swarm-api] {self.address_string()} {fmt % args}")

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
        if isinstance(payload.get("CloseoutContextJson"), str):
            try:
                context = {**context, **json.loads(payload["CloseoutContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "CloseoutContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8087)
    args = p.parse_args()
    print(f"Closeout swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-L3
area: Level 3
rooms:
  walkable: true
  ceilings_complete: true
  systems_operating: true
  safe_access: true
  blocked_rooms: []
punch:
  walk_complete: true
  photos_logged: true
  items_without_owner: []
  open_critical: []
life_safety:
  egress_clear: true
  exit_signs_ok: true
  emergency_lighting_failed: false
  egress_blocked: false
doors:
  function_tested: true
  schedule_mismatches: []
  missing_fire_labels: []
finishes:
  walk_complete: true
  systemic_failures: false
fire_protection:
  required: true
  tests_complete: true
  tests_failed: []
commissioning:
  required: true
  prefunctional_complete: true
  tab_signed: true
  cxa_signed: true
ncr:
  open_high_risk: []
  reinspect_pending: false
docs:
  asbuilts_current: true
  om_complete: true
  warranty_log: true
turnover:
  inspection_log: true
  ncr_summary: true
  certs_packaged: true
  photos_packaged: true
signatures:
  chain_complete: true
  missing_roles: []
tco:
  mock_walk_complete: true
  binder_ready: true
  open_occupancy_rfis: []
crew:
  roles:
    - closeout_lead
    - qa_lead
    - pm_rep
    - trade_rep
    - cx_rep
    - safety_watch
  headcount: 6
  briefing_complete: true
qa:
  pre_hold_points_clear: true
  closeout_hold_points_clear: true
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_closeout_go.yaml", go)
    write(studio / "samples" / "pre_closeout_go.yaml", go)
    write(agents_root / "fixtures" / "open_critical_punch_hold.yaml", """zone_id: DEMO-L3
require_critical_clear: true
rooms:
  walkable: true
  ceilings_complete: true
  systems_operating: true
  safe_access: true
punch:
  walk_complete: true
  photos_logged: true
  items_without_owner: []
  open_critical: [egress-stair-2-handrail, fire-door-3B-label]
crew:
  roles: [closeout_lead, qa_lead, pm_rep, trade_rep, safety_watch]
  briefing_complete: true
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "egress_blocked_abort.yaml", """zone_id: DEMO-L3
life_safety:
  egress_clear: false
  exit_signs_ok: true
  egress_blocked: true
  emergency_lighting_failed: false
doors:
  function_tested: true
  schedule_mismatches: []
  missing_fire_labels: []
fire_protection:
  required: true
  tests_complete: true
  tests_failed: []
qa:
  closeout_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "ncr_open_hold.yaml", """zone_id: DEMO-L3
ncr:
  open_high_risk: [NCR-441-firestop, NCR-512-sprinkler]
  reinspect_pending: true
punch:
  walk_complete: true
  photos_logged: true
  items_without_owner: []
qa:
  closeout_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "turnover_missing_docs_hold.yaml", """zone_id: DEMO-L3
turnover:
  inspection_log: true
  ncr_summary: true
  certs_packaged: false
  photos_packaged: true
docs:
  asbuilts_current: false
  om_complete: true
  warranty_log: true
signatures:
  chain_complete: false
  missing_roles: [CxA, QA_Manager]
ncr:
  open_high_risk: []
commissioning:
  required: true
  prefunctional_complete: true
  tab_signed: true
  cxa_signed: false
crew:
  roles: [closeout_lead, qa_lead, pm_rep, trade_rep, cx_rep, safety_watch]
qa:
  closeout_hold_points_clear: true
""")
    write(agents_root / "fixtures" / "tco_go.yaml", go)

    write(ROOT / "tests" / "test_closeout_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.closeout_swarm.swarm import CloseoutSwarm
from modules.closeout_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "closeout" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(CloseoutSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_closeout_go():
    assert CloseoutSwarm().run("pre-closeout-gate", _load("pre_closeout_go.yaml")).decision == "GO"


def test_open_critical_punch_hold():
    assert CloseoutSwarm().run("pre-closeout-gate", _load("open_critical_punch_hold.yaml")).decision == "HOLD"


def test_egress_blocked_abort():
    assert CloseoutSwarm().run("life-safety-gate", _load("egress_blocked_abort.yaml")).decision == "ABORT"


def test_ncr_open_hold():
    assert CloseoutSwarm().run("ncr-closeout-gate", _load("ncr_open_hold.yaml")).decision == "HOLD"


def test_turnover_missing_docs_hold():
    assert CloseoutSwarm().run("turnover-package-gate", _load("turnover_missing_docs_hold.yaml")).decision == "HOLD"


def test_tco_go():
    assert CloseoutSwarm().run("tco-readiness-gate", _load("tco_go.yaml")).decision == "GO"


def test_punch_walk_go():
    assert CloseoutSwarm().run("punchlist-walk", _load("pre_closeout_go.yaml")).decision == "GO"


def test_turnover_go():
    assert CloseoutSwarm().run("turnover-package-gate", _load("pre_closeout_go.yaml")).decision == "GO"


def test_hold_abort():
    assert CloseoutSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "blocked egress"}).decision == "ABORT"
''')

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "CloseoutTurnover-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
