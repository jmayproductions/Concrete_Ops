#!/usr/bin/env python3
"""Generate masonry field swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("masonry-lead", "MasonryLead", "Owns masonry sequence and final GO/HOLD/ABORT.",
     """You own **masonry** field sequencing (CMU/brick/stone) and assemble GO/HOLD/ABORT.

## Sequence pattern
1. Submittals: mortar/grout mix, unit certs (ASTM C90/C216), rebar/embeds
2. Layout: plumb control, coursing, bond pattern
3. Mortar QC (ASTM C780 class) + joint thickness control
4. Reinforcement clean, spaced, lapped per ACI 530 / TMS
5. Grout lifts ≤ project max (often 5'); consolidate — no voids
6. Flashing, weeps, control joints open (not mortared shut)
7. Hot/cold weather protection; cure before loading

Do not invent mortar slump, psi, or temperatures."""),
    ("materials-submittal", "MaterialsSubmittal", "Owns mortar/grout mixes and unit certifications.",
     """You own masonry materials readiness.

## Checks
- Mortar mix design approved (type N/S/M as specified)
- Grout mix approved
- CMU/brick certs (ASTM C90 / C216 class)
- Reinforcement / embed submittals approved

HOLD missing approvals before first course."""),
    ("layout-coursing", "LayoutCoursing", "Owns control lines, coursing, and bond pattern.",
     """You own masonry layout.

## Checks
- Plumb control lines / grid benchmarks set
- Coursing height lines established
- Bond pattern confirmed
- Drift/misalignment beyond tolerance (e.g. >1/2\" over 10 ft class) => HOLD rework

HOLD missing control lines."""),
    ("mortar-qc", "MortarQc", "Owns mortar consistency, joint thickness, and tooling.",
     """You own mortar field QC.

## Checks
- Mortar consistency / field test when required (ASTM C780 class)
- Bed/head joints typical 3/8\" ±1/8\" (or project)
- Tooling complete; no dry joints
- Reject retempered/expired mortar per project rules

HOLD out-of-spec mortar or joint thickness."""),
    ("reinforcement", "Reinforcement", "Owns bar placement, cleanliness, and lap splices.",
     """You own masonry reinforcement.

## Checks
- Vertical/horizontal rebar spacing per shops
- Bars clean; embed/cover depth OK
- Lap splices per ACI 530 / TMS / design
- Joint reinforcement / ties as specified

HOLD missing or dirty bars in cells to be grouted."""),
    ("grout-lifts", "GroutLifts", "Owns cell grouting lifts, consolidation, and voids.",
     """You own masonry grouting.

## Checks
- Lift height ≤ project max (often 5' / per spec)
- Consolidation complete; no blockages
- Grout strength evidence when required (ASTM C1019 class)
- Cleanouts used when specified

HOLD overheight lifts or suspected voids."""),
    ("flashing-weeps", "FlashingWeeps", "Owns through-wall flashing, weeps, and drainage cavity.",
     """You own masonry drainage plane details.

## Checks
- Through-wall flashing installed at required levels
- Weeps open and spaced per project (rainscreen cavity not blocked)
- End dams / laps sealed
- Control joints full height and not mortared closed

HOLD blocked weeps or missing flashing at critical courses."""),
    ("plumb-tolerance", "PlumbTolerance", "Owns wall plumb, plane, and alignment QA.",
     """You own geometric tolerances.

## Typical acceptance (override with project)
- Plumb ≈ max 1/4\" per 10 ft class
- Plane / bond alignment within project

HOLD walls beyond tolerance before continuing courses or veneer."""),
    ("weather-protect", "WeatherProtect", "Owns hot/cold weather masonry protection.",
     """You own weather protection for masonry.

## Holds
- Frost / freezing of mortar or units without approved cold-weather procedures
- Hot/dry conditions without curing protection (premature drying)
- Active precip saturating unprotected work

Missing weather when required => HOLD."""),
    ("cure-protect", "CureProtect", "Owns curing covers and early load protection.",
     """You own curing / protection after lay-up.

## Checks
- Protection from premature drying (burlap/plastic/fog as specified)
- Early loading / backfill delayed until criteria met
- Efflorescence risk controlled (drainage + curing)

HOLD unprotected green masonry under drying wind/sun when required."""),
    ("rainscreen-veneer", "RainscreenVeneer", "Owns brick/stone veneer cavity and ties.",
     """You own veneer / rainscreen masonry when in scope.

## Checks
- Cavity width clear; insulation/ties per shops
- Tie spacing OK; weeps/vents spaced (e.g. redesign if >600mm class without approval)
- No cavity blockages (moisture lock)

SKIP if no veneer scope. HOLD blocked cavity."""),
    ("embeds-anchors", "EmbedsAnchors", "Owns embeds, anchor bolts, and ledger interfaces.",
     """You own embeds and anchors in masonry.

## Checks
- Embeds placed per shops before grout
- Anchor types/torque when post-installed
- Interfaces to steel/wood ledgers verified

HOLD missing embeds in cells about to be grouted."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work authority for masonry scaffolds and unstable walls.",
     """Stop-work for masonry.

## Immediate ABORT
- Unstable freestanding wall / scaffold failure risk
- Working under unsupported wall without bracing
- Grout/mortar operations creating collapse risk

SafetyFailsafe FAIL => parent Decision ABORT."""),
    ("crew-ops", "CrewOps", "Owns mason crew roles, fatigue, and briefing.",
     """You own masonry crew readiness.

## Typical roles
masonry_lead, mason, tender, rebar_setter, grout_tech, qc_tech, safety_watch

HOLD missing roles or incomplete briefing."""),
    ("qa-inspector", "QaInspector", "Owns masonry hold points, photos, and NCRs.",
     """You own masonry QC evidence.

## Evidence
- Pre-lay hold points clear
- Mortar/grout tests, rebar photos before grout, flashing/weep photos
- NCRs with reinspect

Missing phase evidence => HOLD."""),
    ("control-joints", "ControlJoints", "Owns control/expansion joint placement and continuity.",
     """You own masonry movement joints.

## Checks
- Control joints located per elevations/shops
- Full height; not mortared closed
- Sealant/backer installed when required

HOLD closed or missing required control joints."""),
]

WORKFLOWS = [
    "pre-masonry-gate",
    "layout-coursing-gate",
    "daily-layup-runbook",
    "mortar-qc-check",
    "rebar-pregrout-gate",
    "grout-lift-runbook",
    "flashing-weep-qa",
    "plumb-tolerance-check",
    "veneer-rainscreen-gate",
    "weather-protect-gate",
    "masonry-closeout",
    "hold-abort",
]

ROLES = (
    "masonry_lead",
    "mason",
    "tender",
    "rebar_setter",
    "grout_tech",
    "qc_tech",
    "safety_watch",
)

ORDERS = {
    "pre-masonry-gate": ["materials-submittal", "layout-coursing", "crew-ops", "weather-protect", "safety-failsafe", "qa-inspector"],
    "layout-coursing-gate": ["layout-coursing", "plumb-tolerance", "qa-inspector"],
    "daily-layup-runbook": ["mortar-qc", "layout-coursing", "plumb-tolerance", "weather-protect", "qa-inspector", "safety-failsafe"],
    "mortar-qc-check": ["mortar-qc", "qa-inspector"],
    "rebar-pregrout-gate": ["reinforcement", "embeds-anchors", "qa-inspector", "safety-failsafe"],
    "grout-lift-runbook": ["reinforcement", "grout-lifts", "weather-protect", "qa-inspector", "safety-failsafe"],
    "flashing-weep-qa": ["flashing-weeps", "control-joints", "qa-inspector"],
    "plumb-tolerance-check": ["plumb-tolerance", "layout-coursing", "qa-inspector"],
    "veneer-rainscreen-gate": ["rainscreen-veneer", "flashing-weeps", "qa-inspector", "safety-failsafe"],
    "weather-protect-gate": ["weather-protect", "cure-protect", "safety-failsafe"],
    "masonry-closeout": ["qa-inspector", "plumb-tolerance", "flashing-weeps", "control-joints", "grout-lifts", "cure-protect", "crew-ops"],
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
    Decision: GO | HOLD | ABORT. Prefer MasonryContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: MasonryContextJson
    description: JSON context for masonry zone mortar grout rebar weather
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    MasonryContextJson:
      displayName: Masonry Context JSON
      description: JSON context for masonry construction
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
    agents_root = ROOT / "agents" / "masonry"
    studio = ROOT / "copilot-studio" / "masonry-crew"
    mod = ROOT / "modules" / "masonry_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for Masonry Swarm

From project `construction.md` extractions:

- QA/QC Field Procedures – Masonry Construction (mortar, joints, rebar, grout lifts, curing)
- Masonry workflow / takeoff / red-flag notes (CMU drift, control joints)
- Masonry Cladding w/ Rainscreen (cavity, weeps, ties)
""")
    write(agents_root / "README.md", """# Masonry Swarm (reference twin)

> See [`../../copilot-studio/masonry-crew/`](../../copilot-studio/masonry-crew/) → `START_HERE.md`.

```bash
python -m modules.masonry_swarm.cli list
python -m modules.masonry_swarm.cli run pre-masonry-gate -c agents/masonry/fixtures/pre_masonry_go.yaml
python -m modules.masonry_swarm.api --port 8086
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# Masonry Swarm — Coordinator

Return one GO / HOLD / ABORT for CMU/brick/stone field work.

## Hard rules
1. No lay-up without approved mortar/grout/unit submittals.
2. No grout over unclean/missing rebar or over-height lifts.
3. Weeps/flashing/control joints must remain open/functional.
4. Protect from frost and premature drying.
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
  componentName: MasonrySwarm
kind: GptComponentMetadata
displayName: Masonry Swarm
instructions: |
  You are the Masonry Swarm coordinator for CMU, brick, and stone field work.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect MasonryContextJson; missing critical fields => HOLD (do not invent readings).
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
  - title: Pre-masonry gate
    text: Run pre-masonry-gate for Stair 1 CMU and return GO/HOLD/ABORT.
  - title: Daily lay-up
    text: Run daily-layup-runbook for today's brick veneer on Grid B.
  - title: Rebar pre-grout
    text: Run rebar-pregrout-gate before we grout the elevator core.
  - title: Grout lift
    text: Run grout-lift-runbook — lifts under 5 feet and cells clean?
  - title: Flashing/weeps
    text: Run flashing-weep-qa at the shelf angle course.
  - title: Weather protect
    text: Run weather-protect-gate — cold weather procedures in place?

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: Masonry Swarm
schemaName: masonry_swarm
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
          - Masonry Swarm ready. Ask for pre-masonry-gate, daily-layup-runbook, rebar-pregrout-gate, grout-lift-runbook, flashing-weep-qa, or another named workflow. I return GO / HOLD / ABORT.
          - Masonry online — share wall/zone context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.masonry_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for CMU/brick/stone masonry QA gates.\n")
    write(studio / "START_HERE.md", """# START HERE — Masonry Swarm drop-in

Ready Copilot Studio workspace for masonry field gates.

## 3 steps
1. Open this `masonry-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Masonry Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-masonry-gate…”*.

## Workflows
`pre-masonry-gate`, `layout-coursing-gate`, `daily-layup-runbook`, `mortar-qc-check`, `rebar-pregrout-gate`, `grout-lift-runbook`, `flashing-weep-qa`, `plumb-tolerance-check`, `veneer-rainscreen-gate`, `weather-protect-gate`, `masonry-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.masonry_swarm.api --port 8086
python -m modules.masonry_swarm.cli run pre-masonry-gate -c agents/masonry/fixtures/pre_masonry_go.yaml
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

    agents_src = r'''"""Deterministic specialist gates for masonry construction."""

from __future__ import annotations

from typing import Any

from modules.masonry_swarm.schemas import GateResult

ERECT_ROLES = __ROLES__
DEFAULT_MAX_GROUT_LIFT_FT = 5.0


def _missing(data: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f for f in fields if not data.get(f)]


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class MaterialsSubmittalAgent:
    name = "materials-submittal"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("materials") or {}
        miss = _missing(m, ("mortar_approved", "grout_approved", "units_certified", "rebar_approved"))
        if miss:
            return GateResult(self.name, "HOLD", "Materials incomplete: " + ", ".join(miss), {"materials": m})
        return GateResult(self.name, "PASS", "Mortar/grout/units/rebar submittals clear", {"materials": m})


class LayoutCoursingAgent:
    name = "layout-coursing"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("layout") or {}
        miss = _missing(l, ("control_lines", "coursing_set", "bond_confirmed"))
        if miss:
            return GateResult(self.name, "HOLD", "Layout incomplete: " + ", ".join(miss), {"layout": l})
        if l.get("drift_over_limit"):
            return GateResult(self.name, "HOLD", "Bond/coursing drift over limit — rework", {"layout": l})
        return GateResult(self.name, "PASS", "Layout/coursing clear", {"layout": l})


class MortarQcAgent:
    name = "mortar-qc"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("mortar") or {}
        if m.get("consistency_ok") is False:
            return GateResult(self.name, "HOLD", "Mortar consistency out of spec", {"mortar": m})
        if m.get("joint_thickness_ok") is False:
            return GateResult(self.name, "HOLD", "Joint thickness out of tolerance", {"mortar": m})
        if not m.get("tooled"):
            return GateResult(self.name, "HOLD", "Joints not tooled/accepted", {"mortar": m})
        if m.get("retempered_expired"):
            return GateResult(self.name, "HOLD", "Retempered/expired mortar in use", {"mortar": m})
        return GateResult(self.name, "PASS", "Mortar QC clear", {"mortar": m})


class ReinforcementAgent:
    name = "reinforcement"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        r = ctx.get("rebar") or {}
        miss = _missing(r, ("spacing_ok", "clean", "laps_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Reinforcement incomplete: " + ", ".join(miss), {"rebar": r})
        return GateResult(self.name, "PASS", "Reinforcement clear", {"rebar": r})


class GroutLiftsAgent:
    name = "grout-lifts"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        g = ctx.get("grout") or {}
        if g.get("required") is False:
            return GateResult(self.name, "PASS", "No grout this gate", {"grout": g})
        lift = _num(g.get("lift_ft"))
        max_lift = _num(g.get("max_lift_ft"), DEFAULT_MAX_GROUT_LIFT_FT) or DEFAULT_MAX_GROUT_LIFT_FT
        if lift is not None and lift > max_lift:
            return GateResult(self.name, "HOLD", f"Grout lift {lift}ft > {max_lift}ft max", {"grout": g})
        if g.get("consolidated") is False:
            return GateResult(self.name, "HOLD", "Grout not consolidated / voids suspected", {"grout": g})
        if g.get("voids"):
            return GateResult(self.name, "HOLD", "Grout voids reported", {"grout": g})
        return GateResult(self.name, "PASS", "Grout lifts clear", {"grout": g})


class FlashingWeepsAgent:
    name = "flashing-weeps"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        f = ctx.get("flashing") or {}
        if not f.get("flashing_installed"):
            return GateResult(self.name, "HOLD", "Required through-wall flashing missing", {"flashing": f})
        if f.get("weeps_open") is False:
            return GateResult(self.name, "HOLD", "Weeps blocked or missing", {"flashing": f})
        if f.get("end_dams_ok") is False:
            return GateResult(self.name, "HOLD", "Flashing end dams/laps deficient", {"flashing": f})
        return GateResult(self.name, "PASS", "Flashing/weeps clear", {"flashing": f})


class PlumbToleranceAgent:
    name = "plumb-tolerance"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("plumb") or {}
        if p.get("within_tolerance") is False:
            return GateResult(self.name, "HOLD", f"Plumb/plane out of tolerance: {p.get('notes', 'see survey')}", {"plumb": p})
        if not p.get("checked"):
            return GateResult(self.name, "HOLD", "Plumb checks not recorded", {"plumb": p})
        return GateResult(self.name, "PASS", "Plumb/tolerance clear", {"plumb": p})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        holds = []
        if w.get("freezing") and not w.get("cold_weather_procedures"):
            holds.append("freezing without cold-weather procedures")
        if w.get("hot_dry") and not w.get("hot_weather_protection"):
            holds.append("hot/dry without curing protection")
        if w.get("active_precip") and not w.get("shelter"):
            holds.append("active precip without shelter")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/protection CLEAR", {"weather": w})


class CureProtectAgent:
    name = "cure-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("cure") or {}
        if c.get("required") is False:
            return GateResult(self.name, "PASS", "Cure protection not required", {"cure": c})
        if not c.get("protected"):
            return GateResult(self.name, "HOLD", "Green masonry not protected from drying/frost", {"cure": c})
        if c.get("early_load"):
            return GateResult(self.name, "HOLD", "Early load/backfill before cure criteria", {"cure": c})
        return GateResult(self.name, "PASS", "Cure/protection clear", {"cure": c})


class RainscreenVeneerAgent:
    name = "rainscreen-veneer"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        v = ctx.get("veneer") or {}
        if not v and not ctx.get("require_veneer"):
            return GateResult(self.name, "SKIP", "No veneer scope", {})
        if v.get("cavity_blocked"):
            return GateResult(self.name, "HOLD", "Veneer cavity blocked (moisture lock)", {"veneer": v})
        miss = _missing(v, ("ties_ok", "weeps_spaced_ok"))
        if miss:
            return GateResult(self.name, "HOLD", "Veneer incomplete: " + ", ".join(miss), {"veneer": v})
        return GateResult(self.name, "PASS", "Veneer/rainscreen clear", {"veneer": v})


class EmbedsAnchorsAgent:
    name = "embeds-anchors"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("embeds") or {}
        if not e:
            return GateResult(self.name, "SKIP", "No embeds scope", {})
        if e.get("missing_before_grout"):
            return GateResult(self.name, "HOLD", "Missing embeds in cells to be grouted: " + ", ".join(e["missing_before_grout"]), {"embeds": e})
        return GateResult(self.name, "PASS", "Embeds/anchors clear", {"embeds": e})


class ControlJointsAgent:
    name = "control-joints"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        c = ctx.get("control_joints") or {}
        if not c:
            return GateResult(self.name, "SKIP", "No control joint scope", {})
        if c.get("mortared_closed"):
            return GateResult(self.name, "HOLD", "Control joints mortared closed", {"control_joints": c})
        if not c.get("located_per_shops"):
            return GateResult(self.name, "HOLD", "Control joints not located per shops", {"control_joints": c})
        return GateResult(self.name, "PASS", "Control joints clear", {"control_joints": c})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if ctx.get("wall", {}).get("unstable_unbraced"):
            violations.append("unstable unbraced masonry wall")
        if ctx.get("scaffold", {}).get("unsafe"):
            violations.append("scaffold unsafe")
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
            return GateResult(self.name, "PASS", "Pre-masonry QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class MasonryLeadAgent:
    name = "masonry-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked masonry work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named masonry workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.masonry_swarm.agents import (
    ControlJointsAgent,
    CrewOpsAgent,
    CureProtectAgent,
    EmbedsAnchorsAgent,
    FlashingWeepsAgent,
    GroutLiftsAgent,
    LayoutCoursingAgent,
    MasonryLeadAgent,
    MaterialsSubmittalAgent,
    MortarQcAgent,
    PlumbToleranceAgent,
    QaInspectorAgent,
    RainscreenVeneerAgent,
    ReinforcementAgent,
    SafetyFailsafeAgent,
    WeatherProtectAgent,
)
from modules.masonry_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-masonry-gate",
    "layout-coursing-gate",
    "daily-layup-runbook",
    "mortar-qc-check",
    "rebar-pregrout-gate",
    "grout-lift-runbook",
    "flashing-weep-qa",
    "plumb-tolerance-check",
    "veneer-rainscreen-gate",
    "weather-protect-gate",
    "masonry-closeout",
    "hold-abort",
)


def _decide(gates: list[GateResult]) -> Decision:
    active = [g for g in gates if g.status != "SKIP"]
    if any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in active):
        return "ABORT"
    if any(g.status in ("FAIL", "HOLD") for g in active):
        return "HOLD"
    return "GO"


def _actions(decision: Decision, gates: list[GateResult]) -> list[str]:
    if decision == "GO":
        return ["Proceed to next masonry sequence / workflow", "Maintain cure + weep/flashing protection"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — secure unstable walls/scaffold",
            "Preserve photos, mortar/grout logs, timestamps",
            "Re-enter through pre-masonry-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "masonry-lead"]
    return [
        "Do not advance courses / grout / veneer cover",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.materials = MaterialsSubmittalAgent()
        self.layout = LayoutCoursingAgent()
        self.mortar = MortarQcAgent()
        self.rebar = ReinforcementAgent()
        self.grout = GroutLiftsAgent()
        self.flash = FlashingWeepsAgent()
        self.plumb = PlumbToleranceAgent()
        self.weather = WeatherProtectAgent()
        self.cure = CureProtectAgent()
        self.veneer = RainscreenVeneerAgent()
        self.embeds = EmbedsAnchorsAgent()
        self.cj = ControlJointsAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = MasonryLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_masonry_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.materials.evaluate(ctx),
            self.layout.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-masonry-gate", ctx, gates, {
            "GO": "Pre-masonry clear — lay-up may begin.",
            "HOLD": "Pre-masonry holding — materials/layout/weather.",
            "ABORT": "Pre-masonry aborted by fail-safe.",
        })

    def layout_coursing_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.layout.evaluate(ctx), self.plumb.evaluate(ctx), self.qa.evaluate(ctx, phase="pre")]
        return self._finish("layout-coursing-gate", ctx, gates, {
            "GO": "Layout/coursing clear.",
            "HOLD": "Layout holding.",
            "ABORT": "Layout aborted.",
        })

    def daily_layup_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.mortar.evaluate(ctx),
            self.layout.evaluate(ctx),
            self.plumb.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("daily-layup-runbook", ctx, gates, {
            "GO": "Daily lay-up clear.",
            "HOLD": "Daily lay-up holding.",
            "ABORT": "Daily lay-up aborted.",
        })

    def mortar_qc_check(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.mortar.evaluate(ctx), self.qa.evaluate(ctx, phase="during")]
        return self._finish("mortar-qc-check", ctx, gates, {
            "GO": "Mortar QC clear.",
            "HOLD": "Mortar QC holding.",
            "ABORT": "Mortar QC aborted.",
        })

    def rebar_pregrout_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.rebar.evaluate(ctx),
            self.embeds.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("rebar-pregrout-gate", ctx, gates, {
            "GO": "Rebar pre-grout clear.",
            "HOLD": "Rebar/embeds holding — do not grout.",
            "ABORT": "Rebar gate aborted.",
        })

    def grout_lift_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.rebar.evaluate(ctx),
            self.grout.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("grout-lift-runbook", ctx, gates, {
            "GO": "Grout lift clear.",
            "HOLD": "Grout lift holding.",
            "ABORT": "Grout lift aborted.",
        })

    def flashing_weep_qa(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.flash.evaluate(ctx), self.cj.evaluate(ctx), self.qa.evaluate(ctx, phase="during")]
        return self._finish("flashing-weep-qa", ctx, gates, {
            "GO": "Flashing/weeps/control joints clear.",
            "HOLD": "Flashing/weeps holding.",
            "ABORT": "Flashing aborted.",
        })

    def plumb_tolerance_check(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.plumb.evaluate(ctx), self.layout.evaluate(ctx), self.qa.evaluate(ctx, phase="during")]
        return self._finish("plumb-tolerance-check", ctx, gates, {
            "GO": "Plumb/tolerance clear.",
            "HOLD": "Plumb holding.",
            "ABORT": "Plumb aborted.",
        })

    def veneer_rainscreen_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.veneer.evaluate({**ctx, "require_veneer": True}),
            self.flash.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("veneer-rainscreen-gate", ctx, gates, {
            "GO": "Veneer/rainscreen clear.",
            "HOLD": "Veneer holding.",
            "ABORT": "Veneer aborted.",
        })

    def weather_protect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [self.weather.evaluate(ctx), self.cure.evaluate(ctx), self.safety.evaluate(ctx)]
        return self._finish("weather-protect-gate", ctx, gates, {
            "GO": "Weather/cure protection clear.",
            "HOLD": "Weather/cure holding.",
            "ABORT": "Weather protect aborted.",
        })

    def masonry_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.qa.evaluate(ctx, phase="post"),
            self.plumb.evaluate(ctx),
            self.flash.evaluate(ctx),
            self.cj.evaluate(ctx),
            self.grout.evaluate(ctx),
            self.cure.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("masonry-closeout", ctx, gates, {
            "GO": "Masonry closeout complete.",
            "HOLD": "Masonry closeout incomplete.",
            "ABORT": "Masonry closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        reason = ctx.get("block_reason") or "unspecified gate failure"
        severity = (ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        gates = [GateResult(
            "safety-failsafe" if decision == "ABORT" else "masonry-lead",
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

    write(mod / "swarm.py", '''"""Masonry swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.masonry_swarm.schemas import SwarmResult
from modules.masonry_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class MasonrySwarm:
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
        log_event(f"[masonry-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[masonry-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["MasonrySwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.masonry_swarm.swarm import MasonrySwarm, SwarmResult
from modules.masonry_swarm.workflows import WORKFLOW_IDS

__all__ = ["MasonrySwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for masonry swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.masonry_swarm.swarm import MasonrySwarm

app = typer.Typer(add_completion=False, help="Masonry field swarm")


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
    for w in MasonrySwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = MasonrySwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "masonry" / "fixtures" / "pre_masonry_go.yaml"
    result = MasonrySwarm().run("pre-masonry-gate", yaml.safe_load(fixture.read_text()))
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

from modules.masonry_swarm.swarm import MasonrySwarm
from modules.masonry_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = MasonrySwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[masonry-swarm-api] {self.address_string()} {fmt % args}")

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
        if isinstance(payload.get("MasonryContextJson"), str):
            try:
                context = {**context, **json.loads(payload["MasonryContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "MasonryContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8086)
    args = p.parse_args()
    print(f"Masonry swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-STAIR-1-CMU
area: Stair 1 CMU
materials:
  mortar_approved: true
  grout_approved: true
  units_certified: true
  rebar_approved: true
layout:
  control_lines: true
  coursing_set: true
  bond_confirmed: true
  drift_over_limit: false
mortar:
  consistency_ok: true
  joint_thickness_ok: true
  tooled: true
  retempered_expired: false
rebar:
  spacing_ok: true
  clean: true
  laps_ok: true
grout:
  lift_ft: 4.0
  max_lift_ft: 5.0
  consolidated: true
  voids: false
flashing:
  flashing_installed: true
  weeps_open: true
  end_dams_ok: true
plumb:
  checked: true
  within_tolerance: true
weather:
  freezing: false
  hot_dry: false
  active_precip: false
  cold_weather_procedures: true
  hot_weather_protection: true
cure:
  protected: true
  early_load: false
veneer:
  ties_ok: true
  weeps_spaced_ok: true
  cavity_blocked: false
embeds:
  missing_before_grout: []
control_joints:
  located_per_shops: true
  mortared_closed: false
crew:
  roles:
    - masonry_lead
    - mason
    - tender
    - rebar_setter
    - grout_tech
    - qc_tech
    - safety_watch
  headcount: 8
  briefing_complete: true
  fatigued_workers: []
qa:
  pre_hold_points_clear: true
  install_hold_points_clear: true
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_masonry_go.yaml", go)
    write(studio / "samples" / "pre_masonry_go.yaml", go)
    write(agents_root / "fixtures" / "grout_lift_hold.yaml", """zone_id: DEMO-STAIR-1-CMU
rebar:
  spacing_ok: true
  clean: true
  laps_ok: true
grout:
  lift_ft: 6.5
  max_lift_ft: 5.0
  consolidated: true
weather:
  freezing: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "weeps_blocked_hold.yaml", """zone_id: DEMO-GRID-B-VENEER
flashing:
  flashing_installed: true
  weeps_open: false
  end_dams_ok: true
control_joints:
  located_per_shops: true
  mortared_closed: false
qa:
  install_hold_points_clear: true
""")
    write(agents_root / "fixtures" / "cold_weather_hold.yaml", """zone_id: DEMO-STAIR-1-CMU
materials:
  mortar_approved: true
  grout_approved: true
  units_certified: true
  rebar_approved: true
layout:
  control_lines: true
  coursing_set: true
  bond_confirmed: true
weather:
  freezing: true
  cold_weather_procedures: false
crew:
  roles: [masonry_lead, mason, tender, rebar_setter, grout_tech, qc_tech, safety_watch]
  briefing_complete: true
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "unstable_wall_abort.yaml", """zone_id: DEMO-STAIR-1-CMU
wall:
  unstable_unbraced: true
mortar:
  consistency_ok: true
  joint_thickness_ok: true
  tooled: true
layout:
  control_lines: true
  coursing_set: true
  bond_confirmed: true
plumb:
  checked: true
  within_tolerance: true
weather:
  freezing: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "rebar_dirty_hold.yaml", """zone_id: DEMO-ELEVATOR-CORE
rebar:
  spacing_ok: true
  clean: false
  laps_ok: true
embeds:
  missing_before_grout: [L-12]
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")

    write(ROOT / "tests" / "test_masonry_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.masonry_swarm.swarm import MasonrySwarm
from modules.masonry_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "masonry" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(MasonrySwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_masonry_go():
    assert MasonrySwarm().run("pre-masonry-gate", _load("pre_masonry_go.yaml")).decision == "GO"


def test_grout_lift_hold():
    assert MasonrySwarm().run("grout-lift-runbook", _load("grout_lift_hold.yaml")).decision == "HOLD"


def test_weeps_blocked_hold():
    assert MasonrySwarm().run("flashing-weep-qa", _load("weeps_blocked_hold.yaml")).decision == "HOLD"


def test_cold_weather_hold():
    assert MasonrySwarm().run("pre-masonry-gate", _load("cold_weather_hold.yaml")).decision == "HOLD"


def test_unstable_wall_abort():
    assert MasonrySwarm().run("daily-layup-runbook", _load("unstable_wall_abort.yaml")).decision == "ABORT"


def test_rebar_dirty_hold():
    assert MasonrySwarm().run("rebar-pregrout-gate", _load("rebar_dirty_hold.yaml")).decision == "HOLD"


def test_daily_layup_go():
    assert MasonrySwarm().run("daily-layup-runbook", _load("pre_masonry_go.yaml")).decision == "GO"


def test_closeout_go():
    assert MasonrySwarm().run("masonry-closeout", _load("pre_masonry_go.yaml")).decision == "GO"


def test_hold_abort():
    assert MasonrySwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "scaffold"}).decision == "ABORT"
''')

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "Masonry-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
