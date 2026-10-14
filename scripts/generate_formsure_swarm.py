#!/usr/bin/env python3
"""Generate FormSure / formwork field swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("form-lead", "FormLead", "Owns formwork/pour sequence and final GO/HOLD/ABORT.",
     """You own **FormSure formwork** sequencing and assemble GO/HOLD/ABORT.

## Sequence pattern
1. Form system design + erect + alignment verified
2. Release agent, ties, braces, and leak seals checked
3. Pour drop height and form pressure limits confirmed
4. Shore/props stable during pour and cure
5. Strip only with strength proof; load transfer / reshore as required
6. Post-strip defect/closeout logged

Do not invent maturity strengths, pour rates, or torque values."""),
    ("form-system", "FormSystem", "Owns form system type, design, and pour-rate limits.",
     """You own the formwork system.

## Checks
- System type documented (plywood, steel, modular, gang)
- Design/pour-rate limits known for height and concrete type
- Access/working platforms safe

HOLD pour without approved form system / rate limits."""),
    ("panel-alignment", "PanelAlignment", "Owns plumb, level, square, and alignment.",
     """You own form alignment.

## Checks
- Panels plumb/level/square within tolerance
- Stringline/laser checks logged
- Dimensional control before pour

HOLD pour with unresolved misalignment."""),
    ("release-agent", "ReleaseAgent", "Owns form oil / release coverage.",
     """You own release agent QA.

## Checks
- Uniform coverage; no puddles or dry spots
- Compatible with finish/spec
- Applied before rebar congestion blocks access

HOLD pour with missing/uneven release when required."""),
    ("tie-rods", "TieRods", "Owns tie rods, walers, and tension.",
     """You own form ties.

## Checks
- Tie spacing per form design
- Tension/torque verified
- Missing/loose ties corrected

FAIL/HOLD loose or missing ties before pour."""),
    ("bracing-lateral", "BracingLateral", "Owns lateral braces and kickers.",
     """You own lateral bracing.

## Checks
- Braces installed per design
- Bolt torque / deflection check
- Kickers/anchors secure

HOLD pour with incomplete lateral bracing."""),
    ("leak-seal", "LeakSeal", "Owns joint seals and SCC leak checks.",
     """You own form leak seals.

## Checks
- Seams sealed; sponge/trial leak check for SCC
- Bulkheads tight
- No uncontrolled bleedout paths

HOLD SCC pour with unsealed high-risk seams."""),
    ("pour-drop", "PourDrop", "Owns free-fall / drop height limits.",
     """You own pour drop height.

## Limits (typical)
- Normal concrete ≤ 1.2 m (4 ft) free fall without chute/tremie
- SCC ≤ 0.6 m (2 ft)
- Shotcrete / nozzle methods per method statement

FAIL/HOLD free-fall exceeding limit without controls."""),
    ("form-pressure", "FormPressure", "Owns pour rate vs form design pressure.",
     """You own form pressure control.

## Checks
- Pour rate ≤ design limit for height/temp/mix
- Lift height sequenced
- Pressure monitoring when specified

FAIL intentional over-rate that risks blowout."""),
    ("shoring-props", "ShoringProps", "Owns shores, props, and mudsills.",
     """You own shoring/props.

## Checks
- Props plumb and locked
- Sills bearing; no soft spots
- Mid-pour shake/torque checks as required

HOLD pour/strip on unstable shores."""),
    ("strip-timing", "StripTiming", "Owns strip readiness vs strength.",
     """You own strip timing (ACI 347R pattern).

## Checks
- Min % strength for element type met (walls/columns/slabs/beams)
- Cylinder or maturity proof logged
- Reshore plan when early strip

HOLD/FAIL premature strip without strength proof."""),
    ("load-transfer", "LoadTransfer", "Owns load path after strip / reshore.",
     """You own load transfer QA.

## Checks
- No excessive deflection on release
- Reshores installed before soffit removal when required
- Strip zone logged with strength proof

HOLD load transfer with sagging or missing reshore."""),
    ("panel-reuse", "PanelReuse", "Owns form panel condition for reuse.",
     """You own form reuse condition.

## Checks
- No delamination, warping, or broken edges
- Hardware complete
- Damaged panels tagged out

HOLD reuse of damaged panels for architectural finishes."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work for blowout, collapse, premature strip.",
     """You have stop-work authority. FAIL => swarm **ABORT**.

## Fail conditions
- Blowout / form collapse in progress or imminent
- Pour continuing after loose ties / missing braces flagged critical
- Free-fall or pressure rate grossly exceeded with segregation/blowout risk
- Premature strip under load without strength proof
- Unstable shores with workers at risk"""),
    ("crew-ops", "CrewOps", "Owns formwork crew roles and briefing.",
     """You own form crew readiness.

## Roles
form_lead, carpenter_foreman, form_setter, pour_boss, shore_tech, qc_tech, safety_watch

HOLD missing roles or incomplete form/pour briefing."""),
    ("qa-inspector", "QaInspector", "Owns formwork ITP docs and strip logs.",
     """You own formwork QA evidence.

## Checks
- Pre-pour form checklist signed
- Strength/maturity proof attached before strip
- Defect photos logged post-strip

HOLD missing form/strip documentation."""),
]

WORKFLOWS = [
    "pre-pour-form-gate",
    "form-erect-gate",
    "release-agent-check",
    "tie-brace-gate",
    "scc-leak-gate",
    "pour-drop-gate",
    "form-pressure-gate",
    "shore-stability-gate",
    "strip-readiness-gate",
    "load-transfer-gate",
    "post-strip-closeout",
    "hold-abort",
]

ROLES = (
    "form_lead",
    "carpenter_foreman",
    "form_setter",
    "pour_boss",
    "shore_tech",
    "qc_tech",
    "safety_watch",
)

ORDERS = {
    "pre-pour-form-gate": ["form-system", "panel-alignment", "release-agent", "tie-rods", "bracing-lateral", "crew-ops", "safety-failsafe", "qa-inspector"],
    "form-erect-gate": ["form-system", "panel-alignment", "bracing-lateral", "shoring-props", "qa-inspector", "safety-failsafe"],
    "release-agent-check": ["release-agent", "panel-reuse", "qa-inspector"],
    "tie-brace-gate": ["tie-rods", "bracing-lateral", "form-pressure", "safety-failsafe", "qa-inspector"],
    "scc-leak-gate": ["leak-seal", "release-agent", "tie-rods", "safety-failsafe", "qa-inspector"],
    "pour-drop-gate": ["pour-drop", "form-system", "safety-failsafe", "qa-inspector"],
    "form-pressure-gate": ["form-pressure", "tie-rods", "bracing-lateral", "safety-failsafe", "qa-inspector"],
    "shore-stability-gate": ["shoring-props", "load-transfer", "safety-failsafe", "qa-inspector"],
    "strip-readiness-gate": ["strip-timing", "load-transfer", "shoring-props", "safety-failsafe", "qa-inspector"],
    "load-transfer-gate": ["load-transfer", "strip-timing", "shoring-props", "safety-failsafe", "qa-inspector"],
    "post-strip-closeout": ["qa-inspector", "panel-reuse", "strip-timing", "crew-ops"],
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
    Decision: GO | HOLD | ABORT. Prefer FormContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: FormContextJson
    description: JSON context for formwork erect pour strip
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    FormContextJson:
      displayName: Form Context JSON
      description: JSON context for FormSure formwork
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
    agents_root = ROOT / "agents" / "formsure"
    studio = ROOT / "copilot-studio" / "formsure-crew"
    mod = ROOT / "modules" / "formsure_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for FormSure / Formwork Swarm

From project `construction.md` **FormSure v1.0** and ACI 347R field practice:

- Form erect, release agent, ties/braces, leak seals
- Pour drop height and form pressure limits
- Shore stability, strip timing vs strength, load transfer / reshore
""")
    write(agents_root / "README.md", """# FormSure / Formwork Swarm (reference twin)

> See [`../../copilot-studio/formsure-crew/`](../../copilot-studio/formsure-crew/) → `START_HERE.md`.

```bash
python -m modules.formsure_swarm.cli list
python -m modules.formsure_swarm.cli run pre-pour-form-gate -c agents/formsure/fixtures/pre_pour_go.yaml
python -m modules.formsure_swarm.api --port 8097
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# FormSure Swarm — Coordinator

Return one GO / HOLD / ABORT for formwork erect, pour, and strip operations.

## Hard rules
1. No pour without ties, braces, and alignment clear.
2. Drop height and pour-rate/pressure limits are hard stops.
3. No strip without strength/maturity proof for the element.
4. Blowout / collapse / premature strip under load => ABORT.
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
  componentName: FormSureFormworkSwarm
kind: GptComponentMetadata
displayName: FormSure Formwork Swarm
instructions: |
  You are the FormSure / Formwork Swarm coordinator.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect FormContextJson; missing critical fields => HOLD (do not invent readings).
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
  - title: Pre-pour form gate
    text: Run pre-pour-form-gate for Wall W-B2 and return GO/HOLD/ABORT.
  - title: Strip readiness
    text: Run strip-readiness-gate — maturity at 68% for slab S4.
  - title: Pour drop
    text: Run pour-drop-gate — free fall 5 ft on normal mix.
  - title: Tie/brace
    text: Run tie-brace-gate before CIP wall pour.
  - title: Form pressure
    text: Run form-pressure-gate — rate above design.
  - title: Shore stability
    text: Run shore-stability-gate mid-pour.

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: FormSure Formwork Swarm
schemaName: formsure_formwork_swarm
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
          - FormSure Formwork Swarm ready. Ask for pre-pour-form-gate, strip-readiness-gate, pour-drop-gate, form-pressure-gate, or another named workflow. I return GO / HOLD / ABORT.
          - Formwork online — share zone/element context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.formsure_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for FormSure formwork QA gates.\n")
    write(studio / "START_HERE.md", """# START HERE — FormSure Formwork Swarm drop-in

Ready Copilot Studio workspace for formwork erect / pour / strip field gates.

## 3 steps
1. Open this `formsure-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **FormSure Formwork Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-pour-form-gate…”*.

## Workflows
`pre-pour-form-gate`, `form-erect-gate`, `release-agent-check`, `tie-brace-gate`, `scc-leak-gate`, `pour-drop-gate`, `form-pressure-gate`, `shore-stability-gate`, `strip-readiness-gate`, `load-transfer-gate`, `post-strip-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.formsure_swarm.api --port 8097
python -m modules.formsure_swarm.cli run pre-pour-form-gate -c agents/formsure/fixtures/pre_pour_go.yaml
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

    agents_src = r'''"""Deterministic specialist gates for FormSure formwork."""

from __future__ import annotations

from typing import Any

from modules.formsure_swarm.schemas import GateResult

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


class FormSystemAgent:
    name = "form-system"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("form") or {}
        if not f.get("system_type"):
            return GateResult(self.name, "HOLD", "Form system type not documented", {"form": f})
        if f.get("design_approved") is False:
            return GateResult(self.name, "HOLD", "Form design / pour-rate limits not approved", {"form": f})
        return GateResult(self.name, "PASS", f"Form system clear ({f.get('system_type')})", {"form": f})


class PanelAlignmentAgent:
    name = "panel-alignment"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        a = ctx.get("alignment") or {}
        if a.get("plumb_ok") is False or a.get("level_ok") is False or a.get("square_ok") is False:
            return GateResult(self.name, "HOLD", "Form out of plumb/level/square", {"alignment": a})
        if not a.get("checked"):
            return GateResult(self.name, "HOLD", "Alignment not checked", {"alignment": a})
        return GateResult(self.name, "PASS", "Panel alignment clear", {"alignment": a})


class ReleaseAgentAgent:
    name = "release-agent"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        r = ctx.get("release") or {}
        if r.get("required") is False:
            return GateResult(self.name, "SKIP", "Release agent not required", {})
        if r.get("coverage_ok") is False:
            return GateResult(self.name, "HOLD", "Release agent missing or uneven", {"release": r})
        if not r.get("applied"):
            return GateResult(self.name, "HOLD", "Release agent not applied", {"release": r})
        return GateResult(self.name, "PASS", "Release agent clear", {"release": r})


class TieRodsAgent:
    name = "tie-rods"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("ties") or {}
        if t.get("loose_or_missing"):
            return GateResult(self.name, "FAIL", "Loose or missing form ties", {"ties": t})
        if t.get("tension_ok") is False:
            return GateResult(self.name, "HOLD", "Tie tension/torque not verified", {"ties": t})
        if not t.get("spacing_ok"):
            return GateResult(self.name, "HOLD", "Tie spacing not confirmed per design", {"ties": t})
        return GateResult(self.name, "PASS", "Tie rods clear", {"ties": t})


class BracingLateralAgent:
    name = "bracing-lateral"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("bracing") or {}
        if b.get("incomplete"):
            return GateResult(self.name, "FAIL", "Lateral bracing incomplete/critical", {"bracing": b})
        if b.get("installed") is False:
            return GateResult(self.name, "HOLD", "Lateral braces not installed", {"bracing": b})
        if b.get("torque_ok") is False:
            return GateResult(self.name, "HOLD", "Brace bolt torque/deflection check failed", {"bracing": b})
        return GateResult(self.name, "PASS", "Lateral bracing clear", {"bracing": b})


class LeakSealAgent:
    name = "leak-seal"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("leak") or {}
        mix = (ctx.get("mix") or {}).get("type") or "normal"
        if mix == "scc" and l.get("seams_sealed") is False:
            return GateResult(self.name, "HOLD", "SCC seams not leak-checked/sealed", {"leak": l, "mix": mix})
        if l.get("bleedout_path"):
            return GateResult(self.name, "HOLD", "Uncontrolled bleedout path at bulkhead/seam", {"leak": l})
        return GateResult(self.name, "PASS", "Leak seals clear", {"leak": l})


class PourDropAgent:
    name = "pour-drop"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("drop") or {}
        mix = str((ctx.get("mix") or {}).get("type") or "normal").lower()
        height = _num(d.get("free_fall_m"))
        if height is None:
            return GateResult(self.name, "HOLD", "Drop height not measured", {"drop": d})
        if d.get("chute_or_tremie"):
            return GateResult(self.name, "PASS", "Chute/tremie controls free fall", {"drop": d})
        limit = 0.6 if mix == "scc" else 1.2
        if mix in ("shotcrete", "hpc") and not d.get("direct_method"):
            return GateResult(self.name, "FAIL", "HPC/shotcrete requires direct nozzle/pump method", {"drop": d, "mix": mix})
        if height > limit:
            return GateResult(self.name, "FAIL", f"Free fall {height} m > limit {limit} m for {mix}", {"drop": d, "limit_m": limit})
        return GateResult(self.name, "PASS", f"Drop height clear ({height} m ≤ {limit} m)", {"drop": d})


class FormPressureAgent:
    name = "form-pressure"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("pressure") or {}
        rate = _num(p.get("pour_rate_m_per_hr"))
        limit = _num(p.get("design_rate_m_per_hr"))
        if p.get("blowout_risk"):
            return GateResult(self.name, "FAIL", "Form blowout risk — stop pour", {"pressure": p})
        if rate is not None and limit is not None and rate > limit:
            return GateResult(self.name, "FAIL", f"Pour rate {rate} m/hr > design {limit} m/hr", {"pressure": p})
        if p.get("within_design") is False:
            return GateResult(self.name, "HOLD", "Pour rate/lift height outside design", {"pressure": p})
        return GateResult(self.name, "PASS", "Form pressure clear", {"pressure": p})


class ShoringPropsAgent:
    name = "shoring-props"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("shores") or {}
        if s.get("unstable"):
            return GateResult(self.name, "FAIL", "Unstable shores/props — stop work", {"shores": s})
        if s.get("plumb_locked") is False:
            return GateResult(self.name, "HOLD", "Props not plumb/locked", {"shores": s})
        if s.get("bearing_ok") is False:
            return GateResult(self.name, "HOLD", "Soft mudsill / inadequate bearing", {"shores": s})
        return GateResult(self.name, "PASS", "Shores/props clear", {"shores": s})


class StripTimingAgent:
    name = "strip-timing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("strip") or {}
        if t.get("required") is False:
            return GateResult(self.name, "SKIP", "Strip not requested", {})
        strength = _num(t.get("strength_pct"))
        min_pct = _num(t.get("min_strength_pct"), 70.0) or 70.0
        if not t.get("strength_proof"):
            return GateResult(self.name, "FAIL", "No cylinder/maturity proof for strip", {"strip": t})
        if strength is not None and strength < min_pct:
            return GateResult(self.name, "FAIL", f"Strength {strength}% < min {min_pct}% for strip", {"strip": t})
        if t.get("reshore_required") and not t.get("reshore_ready"):
            return GateResult(self.name, "HOLD", "Reshore required but not ready", {"strip": t})
        return GateResult(self.name, "PASS", "Strip timing clear", {"strip": t})


class LoadTransferAgent:
    name = "load-transfer"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("load_transfer") or {}
        if l.get("sagging"):
            return GateResult(self.name, "FAIL", "Sagging soffit on release — re-support", {"load_transfer": l})
        if l.get("deflection_ok") is False:
            return GateResult(self.name, "HOLD", "Excessive deflection on pull/release test", {"load_transfer": l})
        if l.get("reshore_missing"):
            return GateResult(self.name, "HOLD", "Reshores missing before soffit strip", {"load_transfer": l})
        return GateResult(self.name, "PASS", "Load transfer clear", {"load_transfer": l})


class PanelReuseAgent:
    name = "panel-reuse"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("panels") or {}
        if p.get("damaged"):
            return GateResult(self.name, "HOLD", "Damaged panels tagged — do not reuse for finish work", {"panels": p})
        return GateResult(self.name, "PASS", "Panel reuse condition clear", {"panels": p})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("pressure") or {}).get("blowout_risk"):
            violations.append("form blowout risk")
        if (ctx.get("ties") or {}).get("loose_or_missing") and (ctx.get("bracing") or {}).get("incomplete"):
            violations.append("critical ties and braces compromised")
        elif (ctx.get("ties") or {}).get("loose_or_missing"):
            violations.append("loose/missing form ties")
        elif (ctx.get("bracing") or {}).get("incomplete"):
            violations.append("incomplete lateral bracing")
        d = ctx.get("drop") or {}
        mix = str((ctx.get("mix") or {}).get("type") or "normal").lower()
        height = _num(d.get("free_fall_m"))
        limit = 0.6 if mix == "scc" else 1.2
        if height is not None and height > limit and not d.get("chute_or_tremie"):
            violations.append("free-fall drop limit exceeded")
        p = ctx.get("pressure") or {}
        rate = _num(p.get("pour_rate_m_per_hr"))
        plimit = _num(p.get("design_rate_m_per_hr"))
        if rate is not None and plimit is not None and rate > plimit:
            violations.append("pour rate exceeds form design")
        t = ctx.get("strip") or {}
        strength = _num(t.get("strength_pct"))
        min_pct = _num(t.get("min_strength_pct"), 70.0) or 70.0
        if t.get("required") is not False and t.get("strength_proof") is False:
            violations.append("premature strip without strength proof")
        if t.get("required") is not False and strength is not None and strength < min_pct and t.get("strength_proof"):
            violations.append("premature strip below min strength")
        if (ctx.get("shores") or {}).get("unstable"):
            violations.append("unstable shores with collapse risk")
        if (ctx.get("load_transfer") or {}).get("sagging"):
            violations.append("soffit sagging after release")
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
            return GateResult(self.name, "HOLD", "Form/pour briefing incomplete", {})
        return GateResult(self.name, "PASS", f"Form crew ready headcount={crew.get('headcount', len(roles))}", {})


class QaInspectorAgent:
    name = "qa-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        q = ctx.get("qa") or {}
        if phase == "pre" and q.get("pre_hold_points_clear"):
            return GateResult(self.name, "PASS", "Pre-pour form docs clear", {})
        if phase == "strip" and q.get("strip_docs_clear"):
            return GateResult(self.name, "PASS", "Strip docs clear", {})
        if phase not in ("pre",) and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} form docs clear", {})
        return GateResult(self.name, "HOLD", f"No form QA evidence for phase={phase}", {"qa": q})


class FormLeadAgent:
    name = "form-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked formwork sequence"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Formwork sequence ready for {ctx.get('zone_id', ctx.get('element_id', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named FormSure formwork workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.formsure_swarm.agents import (
    BracingLateralAgent,
    CrewOpsAgent,
    FormLeadAgent,
    FormPressureAgent,
    FormSystemAgent,
    LeakSealAgent,
    LoadTransferAgent,
    PanelAlignmentAgent,
    PanelReuseAgent,
    PourDropAgent,
    QaInspectorAgent,
    ReleaseAgentAgent,
    SafetyFailsafeAgent,
    ShoringPropsAgent,
    StripTimingAgent,
    TieRodsAgent,
)
from modules.formsure_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-pour-form-gate",
    "form-erect-gate",
    "release-agent-check",
    "tie-brace-gate",
    "scc-leak-gate",
    "pour-drop-gate",
    "form-pressure-gate",
    "shore-stability-gate",
    "strip-readiness-gate",
    "load-transfer-gate",
    "post-strip-closeout",
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
        return ["Proceed under form design / pour-rate controls", "Re-check ties, braces, and shores before and during pour"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP POUR/STRIP — secure forms, shores, and exclusion",
            "Preserve checklists, strength proofs, photos, timestamps",
            "Re-enter through pre-pour-form-gate or strip-readiness-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "form-lead"]
    return [
        "Do not pour or strip until cleared",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("element_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.system = FormSystemAgent()
        self.align = PanelAlignmentAgent()
        self.release = ReleaseAgentAgent()
        self.ties = TieRodsAgent()
        self.bracing = BracingLateralAgent()
        self.leak = LeakSealAgent()
        self.drop = PourDropAgent()
        self.pressure = FormPressureAgent()
        self.shores = ShoringPropsAgent()
        self.strip = StripTimingAgent()
        self.load = LoadTransferAgent()
        self.panels = PanelReuseAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = FormLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_pour_form_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.system.evaluate(ctx),
            self.align.evaluate(ctx),
            self.release.evaluate(ctx),
            self.ties.evaluate(ctx),
            self.bracing.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-pour-form-gate", ctx, gates, {
            "GO": "Pre-pour forms clear — placement may proceed under rate/drop controls.",
            "HOLD": "Pre-pour form holding — system/align/ties/braces/release.",
            "ABORT": "Pre-pour form aborted by fail-safe.",
        })

    def form_erect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.system.evaluate(ctx),
            self.align.evaluate(ctx),
            self.bracing.evaluate(ctx),
            self.shores.evaluate(ctx),
            self.qa.evaluate(ctx, phase="erect"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("form-erect-gate", ctx, gates, {
            "GO": "Form erect clear.",
            "HOLD": "Form erect holding.",
            "ABORT": "Form erect aborted.",
        })

    def release_agent_check(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.release.evaluate(ctx),
            self.panels.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("release-agent-check", ctx, gates, {
            "GO": "Release agent check clear.",
            "HOLD": "Release agent holding.",
            "ABORT": "Release agent aborted.",
        })

    def tie_brace_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.ties.evaluate(ctx),
            self.bracing.evaluate(ctx),
            self.pressure.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("tie-brace-gate", ctx, gates, {
            "GO": "Ties and braces clear.",
            "HOLD": "Ties/braces holding.",
            "ABORT": "Ties/braces aborted — do not pour.",
        })

    def scc_leak_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        mix = {**(ctx.get("mix") or {}), "type": (ctx.get("mix") or {}).get("type") or "scc"}
        ctx = {**ctx, "mix": mix}
        gates = [
            self.leak.evaluate(ctx),
            self.release.evaluate(ctx),
            self.ties.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("scc-leak-gate", ctx, gates, {
            "GO": "SCC leak seals clear.",
            "HOLD": "SCC leak holding.",
            "ABORT": "SCC leak aborted.",
        })

    def pour_drop_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.drop.evaluate(ctx),
            self.system.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("pour-drop-gate", ctx, gates, {
            "GO": "Pour drop height clear.",
            "HOLD": "Pour drop holding.",
            "ABORT": "Pour drop aborted — use chute/tremie or lower free fall.",
        })

    def form_pressure_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.pressure.evaluate(ctx),
            self.ties.evaluate(ctx),
            self.bracing.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("form-pressure-gate", ctx, gates, {
            "GO": "Form pressure clear.",
            "HOLD": "Form pressure holding.",
            "ABORT": "Form pressure aborted — slow/stop pour.",
        })

    def shore_stability_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.shores.evaluate(ctx),
            self.load.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("shore-stability-gate", ctx, gates, {
            "GO": "Shore stability clear.",
            "HOLD": "Shore stability holding.",
            "ABORT": "Shore stability aborted.",
        })

    def strip_readiness_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        strip = {**(ctx.get("strip") or {}), "required": True}
        ctx = {**ctx, "strip": strip}
        gates = [
            self.strip.evaluate(ctx),
            self.load.evaluate(ctx),
            self.shores.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="strip"),
        ]
        return self._finish("strip-readiness-gate", ctx, gates, {
            "GO": "Strip readiness clear.",
            "HOLD": "Strip readiness holding.",
            "ABORT": "Strip aborted — premature or unsafe release.",
        })

    def load_transfer_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.load.evaluate(ctx),
            self.strip.evaluate(ctx),
            self.shores.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="strip"),
        ]
        return self._finish("load-transfer-gate", ctx, gates, {
            "GO": "Load transfer clear.",
            "HOLD": "Load transfer holding.",
            "ABORT": "Load transfer aborted.",
        })

    def post_strip_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="strip"),
            self.panels.evaluate(ctx),
            self.strip.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("post-strip-closeout", ctx, gates, {
            "GO": "Post-strip closeout clear.",
            "HOLD": "Post-strip closeout holding.",
            "ABORT": "Post-strip closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "form-lead",
            "FAIL" if decision == "ABORT" else "HOLD",
            reason,
            {"owner": ctx.get("owner", "form_superintendent")},
        )]
        summary = "ABORT escalated — stop pour/strip and secure." if decision == "ABORT" else "HOLD escalated — clear owner action then re-check."
        return SwarmResult("hold-abort", _id(ctx), decision, summary, gates, _actions(decision, gates))


def get_workflow_handlers(runner: WorkflowRunner | None = None) -> dict[str, Callable[[dict[str, Any]], SwarmResult]]:
    r = runner or WorkflowRunner()
    return {wid: getattr(r, wid.replace("-", "_")) for wid in WORKFLOW_IDS}
''')

    write(mod / "swarm.py", '''"""FormSure formwork swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.formsure_swarm.schemas import SwarmResult
from modules.formsure_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class FormSureSwarm:
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
        log_event(f"[formsure-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[formsure-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["FormSureSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.formsure_swarm.swarm import FormSureSwarm, SwarmResult
from modules.formsure_swarm.workflows import WORKFLOW_IDS

__all__ = ["FormSureSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for FormSure formwork swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.formsure_swarm.swarm import FormSureSwarm

app = typer.Typer(add_completion=False, help="FormSure formwork field swarm")


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
    for w in FormSureSwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = FormSureSwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "formsure" / "fixtures" / "pre_pour_go.yaml"
    result = FormSureSwarm().run("pre-pour-form-gate", yaml.safe_load(fixture.read_text()))
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

from modules.formsure_swarm.swarm import FormSureSwarm
from modules.formsure_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = FormSureSwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[formsure-swarm-api] {self.address_string()} {fmt % args}")

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
        if isinstance(payload.get("FormContextJson"), str):
            try:
                context = {**context, **json.loads(payload["FormContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "FormContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8097)
    args = p.parse_args()
    print(f"FormSure formwork swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-WALL-B2
element_id: Wall-B2
form:
  system_type: modular
  design_approved: true
alignment:
  checked: true
  plumb_ok: true
  level_ok: true
  square_ok: true
release:
  required: true
  applied: true
  coverage_ok: true
ties:
  spacing_ok: true
  tension_ok: true
  loose_or_missing: false
bracing:
  installed: true
  torque_ok: true
  incomplete: false
leak:
  seams_sealed: true
  bleedout_path: false
mix:
  type: normal
drop:
  free_fall_m: 0.9
  chute_or_tremie: false
pressure:
  pour_rate_m_per_hr: 1.5
  design_rate_m_per_hr: 2.0
  within_design: true
  blowout_risk: false
shores:
  plumb_locked: true
  bearing_ok: true
  unstable: false
strip:
  required: false
  strength_proof: true
  strength_pct: 85
  min_strength_pct: 70
  reshore_required: false
  reshore_ready: true
load_transfer:
  deflection_ok: true
  sagging: false
  reshore_missing: false
panels:
  damaged: false
crew:
  roles:
    - form_lead
    - carpenter_foreman
    - form_setter
    - pour_boss
    - shore_tech
    - qc_tech
    - safety_watch
  headcount: 10
  briefing_complete: true
qa:
  pre_hold_points_clear: true
  install_hold_points_clear: true
  strip_docs_clear: true
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_pour_go.yaml", go)
    write(studio / "samples" / "pre_pour_go.yaml", go)
    write(agents_root / "fixtures" / "loose_ties_abort.yaml", """zone_id: DEMO-WALL-B2
ties:
  spacing_ok: false
  tension_ok: false
  loose_or_missing: true
bracing:
  installed: true
  torque_ok: true
  incomplete: false
pressure:
  within_design: true
  blowout_risk: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "drop_height_abort.yaml", """zone_id: DEMO-WALL-B2
form:
  system_type: plywood
  design_approved: true
mix:
  type: normal
drop:
  free_fall_m: 1.8
  chute_or_tremie: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "overrate_abort.yaml", """zone_id: DEMO-WALL-B2
ties:
  spacing_ok: true
  tension_ok: true
  loose_or_missing: false
bracing:
  installed: true
  torque_ok: true
  incomplete: false
pressure:
  pour_rate_m_per_hr: 3.5
  design_rate_m_per_hr: 2.0
  within_design: false
  blowout_risk: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "early_strip_abort.yaml", """zone_id: DEMO-SLAB-S4
shores:
  plumb_locked: true
  bearing_ok: true
  unstable: false
strip:
  required: true
  strength_proof: true
  strength_pct: 55
  min_strength_pct: 70
  reshore_required: true
  reshore_ready: false
load_transfer:
  deflection_ok: true
  sagging: false
  reshore_missing: true
qa:
  strip_docs_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "soft_shore_hold.yaml", """zone_id: DEMO-SLAB-S4
shores:
  plumb_locked: false
  bearing_ok: false
  unstable: false
load_transfer:
  deflection_ok: true
  sagging: false
  reshore_missing: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "release_hold.yaml", """zone_id: DEMO-WALL-B2
release:
  required: true
  applied: false
  coverage_ok: false
panels:
  damaged: false
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")

    write(ROOT / "tests" / "test_formsure_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.formsure_swarm.swarm import FormSureSwarm
from modules.formsure_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "formsure" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(FormSureSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_pour_go():
    assert FormSureSwarm().run("pre-pour-form-gate", _load("pre_pour_go.yaml")).decision == "GO"


def test_loose_ties_abort():
    assert FormSureSwarm().run("tie-brace-gate", _load("loose_ties_abort.yaml")).decision == "ABORT"


def test_drop_height_abort():
    assert FormSureSwarm().run("pour-drop-gate", _load("drop_height_abort.yaml")).decision == "ABORT"


def test_overrate_abort():
    assert FormSureSwarm().run("form-pressure-gate", _load("overrate_abort.yaml")).decision == "ABORT"


def test_early_strip_abort():
    assert FormSureSwarm().run("strip-readiness-gate", _load("early_strip_abort.yaml")).decision == "ABORT"


def test_soft_shore_hold():
    assert FormSureSwarm().run("shore-stability-gate", _load("soft_shore_hold.yaml")).decision == "HOLD"


def test_release_hold():
    assert FormSureSwarm().run("release-agent-check", _load("release_hold.yaml")).decision == "HOLD"


def test_closeout_go():
    assert FormSureSwarm().run("post-strip-closeout", _load("pre_pour_go.yaml")).decision == "GO"


def test_hold_abort():
    assert FormSureSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "blowout"}).decision == "ABORT"
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

### FormSure / Formwork Swarm (Copilot Studio)

Same pattern — field GO/HOLD/ABORT for form erect, pour pressure/drop, and strip:

- [`copilot-studio/formsure-crew/`](copilot-studio/formsure-crew/) — parent + 16 child agents; open `START_HERE.md`
- Drop-in zip: [`packages/FormSureFormwork-Swarm-CopilotStudio-DropIn.zip`](packages/FormSureFormwork-Swarm-CopilotStudio-DropIn.zip)

```bash
python -m modules.formsure_swarm.api --port 8097
python -m modules.formsure_swarm.cli run pre-pour-form-gate -c agents/formsure/fixtures/pre_pour_go.yaml
```
"""
        if "FormSure / Formwork Swarm" not in rtxt and marker in rtxt:
            readme.write_text(rtxt.replace(marker, block + "\n", 1))

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "FormSureFormwork-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
