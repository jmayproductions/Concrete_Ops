#!/usr/bin/env python3
"""Generate SOE / shoring / excavation-support field swarm (Studio + Python twin + zip)."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPECIALISTS = [
    ("soe-lead", "SoeLead", "Owns SOE sequence and final GO/HOLD/ABORT.",
     """You own **support of excavation (SOE) / shoring** sequencing and assemble GO/HOLD/ABORT.

## Sequence pattern
1. PE-stamped SOE design + submittals approved
2. Install piles/sheets; lagging as excavate proceeds
3. Excavate only to allowed stage depths
4. Install wales/struts or tiebacks per stage drawing
5. Proof/performance test anchors; monitor loads/deflection
6. Dewatering as designed; keep excavation dry/stable
7. Brace release only per engineered sequence

Do not invent design loads, stage depths, or monitoring readings."""),
    ("design-submittal", "DesignSubmittal", "Owns PE SOE design and material submittals.",
     """You own SOE design readiness.

## Checks
- PE-stamped SOE drawings/calcs approved
- Soldier pile / sheet / lagging / strut / tieback products approved
- Monitoring plan approved

HOLD missing PE design or critical product approvals before install."""),
    ("survey-monitoring", "SurveyMonitoring", "Owns optical survey, inclinometers, and alarm thresholds.",
     """You own SOE geometric monitoring.

## Checks
- Baseline survey/inclinometers established before excavate
- Readings current to monitoring frequency
- Deflection within alarm/alert limits
- Exceedance => HOLD stop excavate / eng review (may escalate ABORT via safety)

HOLD missing baselines or skipped required readings."""),
    ("soldier-piles", "SoldierPiles", "Owns soldier pile install, plumb, and tip.",
     """You own soldier pile installation.

## Checks
- Location/plumb within tolerance
- Tip elevation / embedment met
- Concrete/grout in pile holes when specified

HOLD piles short of tip or out of tolerance before lagging/excavate."""),
    ("lagging", "Lagging", "Owns timber/shotcrete lagging continuity behind piles.",
     """You own lagging.

## Checks
- Lagging tight to ground; gaps backfilled/packed
- Installed promptly as excavate exposes face
- Thickness/grade per design

HOLD exposed face without lagging beyond allowed height/time."""),
    ("sheet-pile", "SheetPile", "Owns sheet pile drive, interlock, and tip.",
     """You own sheet pile walls.

## Checks
- Interlocks engaged; no lost sheets
- Tip/refusal per design
- Alignment/plumb within tolerance

HOLD broken interlocks or tip short without eng direction."""),
    ("wales-struts", "WalesStruts", "Owns wales, struts, and preload.",
     """You own internal bracing.

## Checks
- Wale/strut installed at design elevation before deeper excavate
- Connections/pins complete; camber/preload applied when specified
- No damaged or undersized members

HOLD excavate past stage without required strut/waler."""),
    ("tiebacks-anchors", "TiebacksAnchors", "Owns tieback drill, grout, and proof/performance tests.",
     """You own ground anchors / tiebacks.

## Checks
- Drill length/angle per design; grout records complete
- Proof/performance tests meet criteria before lock-off
- Corrosion protection / free length as specified

HOLD failed tests or lock-off without passing proof test."""),
    ("excavation-stages", "ExcavationStages", "Owns staged dig depths vs design sequence.",
     """You own excavation staging.

## Checks
- Current dig depth ≤ allowed stage depth
- Prior stage braces/anchors locked off before next cut
- Spoil setbacks maintained

HOLD over-excavation past design stage."""),
    ("dewatering", "Dewatering", "Owns dewatering system and water control.",
     """You own dewatering / groundwater control.

## Checks
- System running per design before/during excavate
- Drawdown targets met; no uncontrolled inflow eroding face
- Discharge permits / treatment when required

HOLD uncontrolled water or offline dewatering when required."""),
    ("load-monitoring", "LoadMonitoring", "Owns strut/anchor load cells and threshold response.",
     """You own load monitoring.

## Checks
- Required load cells active and calibrated
- Loads within design envelope
- Alarm response procedure followed

HOLD missing required load data or unexplained overload."""),
    ("brace-release", "BraceRelease", "Owns engineered brace/strut/tieback release sequence.",
     """You own brace release / SOE removal.

## Checks
- Permanent structure capable of taking load (slab/walls) before release
- Release order matches PE sequence
- Monitoring during/after release

HOLD out-of-sequence release or premature removal."""),
    ("weather-protect", "WeatherProtect", "Owns storm, freeze, and surcharge weather holds.",
     """You own weather/surcharge holds for SOE.

## Holds
- Storm with flooding/erosion risk to face or sumps
- Freeze-thaw degrading lagging/ground without protection
- Unplanned surcharge (stockpile/equipment) at crest

HOLD adverse weather or surcharge before deeper excavate."""),
    ("safety-failsafe", "SafetyFailsafe", "Stop-work for collapse risk, alarms, and open excavation.",
     """You have stop-work authority. FAIL => swarm **ABORT**.

## Fail conditions
- Monitoring alarm exceedance ignored / continued excavate
- Unsupported face / missing brace under design stage load
- Fall hazard — unprotected excavation edge
- Imminent collapse indicators (bulging lagging, cracked crest)
- Utility strike during pile/sheet/anchor install"""),
    ("crew-ops", "CrewOps", "Owns roles, briefing, and fatigue for SOE crews.",
     """You own crew readiness.

## Roles
soe_lead, pile_op, excavator_op, welder_fitter, anchor_crew, qc_tech, safety_watch

HOLD missing roles, incomplete briefing, or fatigue risk."""),
    ("qa-inspector", "QaInspector", "Owns ITP hold points and SOE install records.",
     """You own SOE QA evidence.

## Checks
- Pre-install hold points signed
- Stage logs (depth, brace install, tests) complete
- NCRs dispositioned before next stage/release

HOLD missing ITP evidence."""),
]

WORKFLOWS = [
    "pre-soe-gate",
    "pile-install-runbook",
    "lagging-install-gate",
    "excavation-stage-gate",
    "strut-waler-gate",
    "tieback-test-gate",
    "monitoring-alarm-gate",
    "dewatering-gate",
    "brace-release-gate",
    "weather-protect-gate",
    "soe-closeout",
    "hold-abort",
]

ROLES = (
    "soe_lead",
    "pile_op",
    "excavator_op",
    "welder_fitter",
    "anchor_crew",
    "qc_tech",
    "safety_watch",
)

ORDERS = {
    "pre-soe-gate": ["design-submittal", "survey-monitoring", "crew-ops", "weather-protect", "safety-failsafe", "qa-inspector"],
    "pile-install-runbook": ["design-submittal", "soldier-piles", "sheet-pile", "survey-monitoring", "safety-failsafe", "qa-inspector"],
    "lagging-install-gate": ["lagging", "excavation-stages", "safety-failsafe", "qa-inspector"],
    "excavation-stage-gate": ["excavation-stages", "wales-struts", "tiebacks-anchors", "survey-monitoring", "dewatering", "safety-failsafe", "qa-inspector"],
    "strut-waler-gate": ["wales-struts", "load-monitoring", "survey-monitoring", "qa-inspector", "safety-failsafe"],
    "tieback-test-gate": ["tiebacks-anchors", "load-monitoring", "qa-inspector", "safety-failsafe"],
    "monitoring-alarm-gate": ["survey-monitoring", "load-monitoring", "safety-failsafe", "qa-inspector"],
    "dewatering-gate": ["dewatering", "excavation-stages", "weather-protect", "qa-inspector"],
    "brace-release-gate": ["brace-release", "survey-monitoring", "load-monitoring", "safety-failsafe", "qa-inspector"],
    "weather-protect-gate": ["weather-protect", "dewatering", "safety-failsafe"],
    "soe-closeout": ["qa-inspector", "survey-monitoring", "brace-release", "load-monitoring", "crew-ops"],
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
    Decision: GO | HOLD | ABORT. Prefer SoeContextJson evidence; missing critical fields => HOLD.


inputs:
  - kind: AutomaticTaskInput
    propertyName: SoeContextJson
    description: JSON context for SOE shoring stages braces monitoring
  - kind: AutomaticTaskInput
    propertyName: WorkflowId
    description: Named workflow id being executed

inputType:
  properties:
    SoeContextJson:
      displayName: SOE Context JSON
      description: JSON context for support of excavation
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
    agents_root = ROOT / "agents" / "soe"
    studio = ROOT / "copilot-studio" / "soe-crew"
    mod = ROOT / "modules" / "soe_swarm"

    write(agents_root / "SOURCES.md", """# Source basis for SOE / Shoring Swarm

From project `construction.md` extractions and typical SOE ITP practice:

- QA/QC Field Procedures – Support of Excavation / soldier piles & lagging
- Internal bracing and tieback proof/performance testing
- Staged excavation limits, monitoring alarms, brace release sequence
""")
    write(agents_root / "README.md", """# SOE / Shoring Swarm (reference twin)

> See [`../../copilot-studio/soe-crew/`](../../copilot-studio/soe-crew/) → `START_HERE.md`.

```bash
python -m modules.soe_swarm.cli list
python -m modules.soe_swarm.cli run pre-soe-gate -c agents/soe/fixtures/pre_soe_go.yaml
python -m modules.soe_swarm.api --port 8090
```
""")

    for slug, folder, desc, instr in SPECIALISTS:
        write(agents_root / "instructions" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")
        write(studio / "agents" / folder / "agent.mcs.yml", child_mcs(folder, desc, instr))
        write(studio / "knowledge" / "files" / f"{slug}.md", f"# {folder}\n\n{desc}\n\n{instr}\n")

    root = """# SOE / Shoring Swarm — Coordinator

Return one GO / HOLD / ABORT for support of excavation.

## Hard rules
1. No excavate without PE SOE design + monitoring baseline.
2. Never dig past allowed stage without braces/anchors locked.
3. Respond to monitoring/load alarms — do not ignore.
4. Brace release only per engineered sequence after permanent structure ready.
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
  componentName: SoeShoringSwarm
kind: GptComponentMetadata
displayName: SOE Shoring Swarm
instructions: |
  You are the SOE / Shoring Swarm coordinator for support of excavation.
  Return a single GO / HOLD / ABORT decision with evidence.

  ## Child agents
  {children}.

  ## Orchestration pattern (mandatory)
  1. Identify WorkflowId (ask once if unclear).
  2. Collect SoeContextJson; missing critical fields => HOLD (do not invent readings).
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
  - title: Pre-SOE gate
    text: Run pre-soe-gate for Basement SOE Grid A and return GO/HOLD/ABORT.
  - title: Excavation stage
    text: Run excavation-stage-gate — are we clear to dig to Stage 2?
  - title: Strut/waler
    text: Run strut-waler-gate before next cut.
  - title: Tieback test
    text: Run tieback-test-gate for anchors A-12 to A-18.
  - title: Monitoring alarm
    text: Run monitoring-alarm-gate — inclinometer alert on Wall North.
  - title: Brace release
    text: Run brace-release-gate after B1 slab pour.

aISettings:
  model:
    modelNameHint: GPT5Chat
""")
    write(studio / "settings.mcs.yml", """displayName: SOE Shoring Swarm
schemaName: soe_shoring_swarm
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
          - SOE Shoring Swarm ready. Ask for pre-soe-gate, excavation-stage-gate, strut-waler-gate, tieback-test-gate, monitoring-alarm-gate, brace-release-gate, or another named workflow. I return GO / HOLD / ABORT.
          - SOE online — share wall/stage context and the gate to run.
""")
    write(studio / "actions" / "README.md", "Wire Power Automate / MCP later to `python -m modules.soe_swarm.api` if desired.\n")
    write(studio / "README.md", "Open **START_HERE.md** first.\n\nField swarm for SOE / shoring QA gates.\n")
    write(studio / "START_HERE.md", """# START HERE — SOE Shoring Swarm drop-in

Ready Copilot Studio workspace for support-of-excavation field gates.

## 3 steps
1. Open this `soe-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **SOE Shoring Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-soe-gate…”*.

## Workflows
`pre-soe-gate`, `pile-install-runbook`, `lagging-install-gate`, `excavation-stage-gate`, `strut-waler-gate`, `tieback-test-gate`, `monitoring-alarm-gate`, `dewatering-gate`, `brace-release-gate`, `weather-protect-gate`, `soe-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.soe_swarm.api --port 8090
python -m modules.soe_swarm.cli run pre-soe-gate -c agents/soe/fixtures/pre_soe_go.yaml
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

    agents_src = r'''"""Deterministic specialist gates for SOE / shoring."""

from __future__ import annotations

from typing import Any

from modules.soe_swarm.schemas import GateResult

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


class DesignSubmittalAgent:
    name = "design-submittal"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("design") or {}
        miss = _missing(d, ("pe_stamped_approved", "products_approved", "monitoring_plan_approved"))
        if miss:
            return GateResult(self.name, "HOLD", "SOE design/submittals incomplete: " + ", ".join(miss), {"design": d})
        return GateResult(self.name, "PASS", "PE SOE design/submittals clear", {"design": d})


class SurveyMonitoringAgent:
    name = "survey-monitoring"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        m = ctx.get("monitoring") or {}
        if not m.get("baseline_set"):
            return GateResult(self.name, "HOLD", "Monitoring baseline not established", {"monitoring": m})
        if m.get("readings_current") is False:
            return GateResult(self.name, "HOLD", "Required monitoring readings overdue", {"monitoring": m})
        if m.get("alarm_exceeded"):
            return GateResult(self.name, "FAIL", "Monitoring alarm exceeded — stop excavate / eng review", {"monitoring": m})
        if m.get("alert_exceeded"):
            return GateResult(self.name, "HOLD", "Monitoring alert exceeded — eng review before deeper dig", {"monitoring": m})
        return GateResult(self.name, "PASS", "Survey/monitoring clear", {"monitoring": m})


class SoldierPilesAgent:
    name = "soldier-piles"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        p = ctx.get("soldier_piles") or {}
        if p.get("required") is False:
            return GateResult(self.name, "SKIP", "No soldier piles this gate", {})
        if p.get("tip_ok") is False:
            return GateResult(self.name, "HOLD", "Soldier pile tip/embedment short", {"soldier_piles": p})
        if p.get("plumb_ok") is False:
            return GateResult(self.name, "HOLD", "Soldier pile plumb/location out of tolerance", {"soldier_piles": p})
        return GateResult(self.name, "PASS", "Soldier piles clear", {"soldier_piles": p})


class LaggingAgent:
    name = "lagging"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("lagging") or {}
        if l.get("required") is False:
            return GateResult(self.name, "SKIP", "No lagging scope", {})
        if l.get("exposed_face_over_limit"):
            return GateResult(self.name, "HOLD", "Exposed face without lagging beyond allowed height/time", {"lagging": l})
        if l.get("gaps_unpacked"):
            return GateResult(self.name, "HOLD", "Lagging gaps not packed/backfilled", {"lagging": l})
        if not l.get("installed_ok"):
            return GateResult(self.name, "HOLD", "Lagging not installed/accepted", {"lagging": l})
        return GateResult(self.name, "PASS", "Lagging clear", {"lagging": l})


class SheetPileAgent:
    name = "sheet-pile"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("sheet_pile") or {}
        if s.get("required") is False:
            return GateResult(self.name, "SKIP", "No sheet pile this gate", {})
        if s.get("interlock_broken"):
            return GateResult(self.name, "HOLD", "Sheet interlocks broken/lost", {"sheet_pile": s})
        if s.get("tip_ok") is False and not s.get("eng_direction"):
            return GateResult(self.name, "HOLD", "Sheet tip short without eng direction", {"sheet_pile": s})
        return GateResult(self.name, "PASS", "Sheet pile clear", {"sheet_pile": s})


class WalesStrutsAgent:
    name = "wales-struts"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("bracing") or {}
        if w.get("required") is False:
            return GateResult(self.name, "SKIP", "No internal bracing this gate", {})
        if w.get("missing_for_stage"):
            return GateResult(self.name, "FAIL", "Required wale/strut missing for current/next stage", {"bracing": w})
        if w.get("connections_ok") is False:
            return GateResult(self.name, "HOLD", "Brace connections/pins incomplete", {"bracing": w})
        if w.get("preload_ok") is False:
            return GateResult(self.name, "HOLD", "Required preload/camber not applied", {"bracing": w})
        return GateResult(self.name, "PASS", "Wales/struts clear", {"bracing": w})


class TiebacksAnchorsAgent:
    name = "tiebacks-anchors"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        t = ctx.get("tiebacks") or {}
        if t.get("required") is False:
            return GateResult(self.name, "SKIP", "No tiebacks this gate", {})
        if t.get("required_for_stage") and not t.get("locked_off"):
            return GateResult(self.name, "HOLD", "Stage tiebacks not locked off", {"tiebacks": t})
        if t.get("proof_test_pass") is False:
            return GateResult(self.name, "HOLD", "Tieback proof/performance test failed", {"tiebacks": t})
        if t.get("grout_records_ok") is False:
            return GateResult(self.name, "HOLD", "Anchor grout records incomplete", {"tiebacks": t})
        return GateResult(self.name, "PASS", "Tiebacks/anchors clear", {"tiebacks": t})


class ExcavationStagesAgent:
    name = "excavation-stages"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        e = ctx.get("excavation") or {}
        depth = _num(e.get("current_depth_ft"))
        allowed = _num(e.get("allowed_depth_ft"))
        if depth is not None and allowed is not None and depth > allowed + 1e-6:
            return GateResult(self.name, "FAIL", f"Over-excavated {depth}ft > allowed {allowed}ft stage", {"excavation": e})
        if e.get("prior_braces_incomplete"):
            return GateResult(self.name, "HOLD", "Prior stage braces/anchors incomplete before next cut", {"excavation": e})
        if e.get("spoil_at_crest"):
            return GateResult(self.name, "HOLD", "Spoil surcharge at crest — pull back", {"excavation": e})
        return GateResult(self.name, "PASS", "Excavation stage clear", {"excavation": e})


class DewateringAgent:
    name = "dewatering"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        d = ctx.get("dewatering") or {}
        if d.get("required") is False:
            return GateResult(self.name, "PASS", "Dewatering not required", {"dewatering": d})
        if d.get("system_running") is False:
            return GateResult(self.name, "HOLD", "Dewatering system offline when required", {"dewatering": d})
        if d.get("uncontrolled_inflow"):
            return GateResult(self.name, "HOLD", "Uncontrolled inflow eroding face/bottom", {"dewatering": d})
        if d.get("drawdown_ok") is False:
            return GateResult(self.name, "HOLD", "Drawdown targets not met", {"dewatering": d})
        return GateResult(self.name, "PASS", "Dewatering clear", {"dewatering": d})


class LoadMonitoringAgent:
    name = "load-monitoring"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        l = ctx.get("loads") or {}
        if l.get("required") is False:
            return GateResult(self.name, "PASS", "Load monitoring not required", {"loads": l})
        if not l.get("cells_active"):
            return GateResult(self.name, "HOLD", "Required load cells inactive/missing", {"loads": l})
        if l.get("overload"):
            return GateResult(self.name, "FAIL", "Strut/anchor overload alarm", {"loads": l})
        return GateResult(self.name, "PASS", "Load monitoring clear", {"loads": l})


class BraceReleaseAgent:
    name = "brace-release"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        b = ctx.get("release") or {}
        if b.get("required") is False:
            return GateResult(self.name, "SKIP", "No brace release this gate", {})
        if b.get("sequence_ok") is False:
            return GateResult(self.name, "FAIL", "Out-of-sequence brace release", {"release": b})
        if not b.get("permanent_structure_ready"):
            return GateResult(self.name, "HOLD", "Permanent structure not ready to take load", {"release": b})
        if not b.get("monitoring_during"):
            return GateResult(self.name, "HOLD", "Monitoring not active during/after release", {"release": b})
        return GateResult(self.name, "PASS", "Brace release sequence clear", {"release": b})


class WeatherProtectAgent:
    name = "weather-protect"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        w = ctx.get("weather") or {}
        if not w:
            return GateResult(self.name, "HOLD", "No weather data", {})
        holds = []
        if w.get("storm_flood_risk") and not w.get("sumps_protected"):
            holds.append("storm/flood risk without sump/face protection")
        if w.get("freeze_thaw") and not w.get("face_protected"):
            holds.append("freeze-thaw without face protection")
        if w.get("crest_surcharge"):
            holds.append("unplanned crest surcharge")
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"weather": w})
        return GateResult(self.name, "PASS", "Weather/protection CLEAR", {"weather": w})


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        s = ctx.get("safety") or {}
        violations = list(s.get("violations") or [])
        if (ctx.get("monitoring") or {}).get("alarm_exceeded") and (ctx.get("excavation") or {}).get("continuing_after_alarm"):
            violations.append("monitoring alarm ignored — continued excavate")
        if (ctx.get("bracing") or {}).get("missing_for_stage"):
            violations.append("unsupported excavation — missing brace")
        if (ctx.get("edge") or {}).get("unprotected"):
            violations.append("unprotected excavation edge fall hazard")
        if (ctx.get("face") or {}).get("collapse_indicators"):
            violations.append("imminent collapse indicators on face/crest")
        if (ctx.get("utilities") or {}).get("utility_strike"):
            violations.append("utility strike during SOE install")
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
            return GateResult(self.name, "PASS", "Pre-SOE QA hold points clear", {})
        if phase != "pre" and q.get("install_hold_points_clear"):
            return GateResult(self.name, "PASS", f"{phase} QA clear", {})
        return GateResult(self.name, "HOLD", f"No QA evidence for phase={phase}", {"qa": q})


class SoeLeadAgent:
    name = "soe-lead"

    def assemble(self, ctx: dict[str, Any], gates: list[GateResult], workflow: str) -> GateResult:
        active = [g for g in gates if g.status != "SKIP"]
        if any(g.status == "FAIL" for g in active):
            hint, detail = "ABORT", "Fail-safe blocked SOE work"
        elif any(g.status in ("FAIL", "HOLD") for g in active):
            blockers = [g.agent for g in active if g.status in ("FAIL", "HOLD")]
            hint, detail = "HOLD", "Blocked by: " + ", ".join(blockers)
        else:
            hint, detail = "GO", f"Sequence ready for {ctx.get('zone_id', ctx.get('area', 'zone'))}"
        status: Any = "PASS" if hint == "GO" else ("FAIL" if hint == "ABORT" else "HOLD")
        return GateResult(self.name, status, f"{detail} [{hint}]", {"decision_hint": hint, "workflow": workflow})
'''
    write(mod / "agents.py", agents_src.replace("__ROLES__", repr(ROLES)))

    write(mod / "workflows.py", '''"""Named SOE / shoring workflow runners."""

from __future__ import annotations

from typing import Any, Callable

from modules.soe_swarm.agents import (
    BraceReleaseAgent,
    CrewOpsAgent,
    DesignSubmittalAgent,
    DewateringAgent,
    ExcavationStagesAgent,
    LaggingAgent,
    LoadMonitoringAgent,
    QaInspectorAgent,
    SafetyFailsafeAgent,
    SheetPileAgent,
    SoeLeadAgent,
    SoldierPilesAgent,
    SurveyMonitoringAgent,
    TiebacksAnchorsAgent,
    WalesStrutsAgent,
    WeatherProtectAgent,
)
from modules.soe_swarm.schemas import Decision, GateResult, SwarmResult

WORKFLOW_IDS = (
    "pre-soe-gate",
    "pile-install-runbook",
    "lagging-install-gate",
    "excavation-stage-gate",
    "strut-waler-gate",
    "tieback-test-gate",
    "monitoring-alarm-gate",
    "dewatering-gate",
    "brace-release-gate",
    "weather-protect-gate",
    "soe-closeout",
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
        return ["Proceed to next SOE sequence / workflow", "Keep monitoring + stage logs current"]
    if decision == "ABORT":
        fails = [g for g in gates if g.status == "FAIL"]
        return [
            "STOP WORK — backfill/secure face; clear exclusion zone; call engineer",
            "Preserve monitoring plots, stage depths, photos, timestamps",
            "Re-enter through pre-soe-gate after corrective action",
            *[f"Resolve {g.agent}: {g.detail}" for g in fails],
        ]
    holds = [g for g in gates if g.status in ("FAIL", "HOLD") and g.agent != "soe-lead"]
    return [
        "Do not deepen excavate / release braces",
        *[f"Clear {g.agent}: {g.detail}" for g in holds],
        "Re-run failed gates + safety-failsafe before release",
    ]


def _id(ctx: dict[str, Any]) -> str:
    return ctx.get("zone_id") or ctx.get("area") or "ZONE-UNSET"


class WorkflowRunner:
    def __init__(self) -> None:
        self.design = DesignSubmittalAgent()
        self.monitoring = SurveyMonitoringAgent()
        self.soldier = SoldierPilesAgent()
        self.lagging = LaggingAgent()
        self.sheet = SheetPileAgent()
        self.bracing = WalesStrutsAgent()
        self.tiebacks = TiebacksAnchorsAgent()
        self.excavation = ExcavationStagesAgent()
        self.dewatering = DewateringAgent()
        self.loads = LoadMonitoringAgent()
        self.release = BraceReleaseAgent()
        self.weather = WeatherProtectAgent()
        self.safety = SafetyFailsafeAgent()
        self.crew = CrewOpsAgent()
        self.qa = QaInspectorAgent()
        self.lead = SoeLeadAgent()

    def _finish(self, workflow: str, ctx: dict[str, Any], gates: list[GateResult], summaries: dict[str, str]) -> SwarmResult:
        gates.append(self.lead.assemble(ctx, gates, workflow))
        decision = _decide(gates)
        return SwarmResult(workflow, _id(ctx), decision, summaries[decision], gates, _actions(decision, gates))

    def pre_soe_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.design.evaluate(ctx),
            self.monitoring.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=True),
            self.weather.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="pre"),
        ]
        return self._finish("pre-soe-gate", ctx, gates, {
            "GO": "Pre-SOE clear — install/excavate sequence may proceed.",
            "HOLD": "Pre-SOE holding — design/monitoring/weather.",
            "ABORT": "Pre-SOE aborted by fail-safe.",
        })

    def pile_install_runbook(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.design.evaluate(ctx),
            self.soldier.evaluate(ctx),
            self.sheet.evaluate(ctx),
            self.monitoring.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("pile-install-runbook", ctx, gates, {
            "GO": "Pile/sheet install clear.",
            "HOLD": "Pile/sheet install holding.",
            "ABORT": "Pile/sheet install aborted.",
        })

    def lagging_install_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "lagging": {**(ctx.get("lagging") or {}), "required": True}}
        gates = [
            self.lagging.evaluate(ctx),
            self.excavation.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("lagging-install-gate", ctx, gates, {
            "GO": "Lagging install clear.",
            "HOLD": "Lagging holding.",
            "ABORT": "Lagging aborted.",
        })

    def excavation_stage_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.excavation.evaluate(ctx),
            self.bracing.evaluate(ctx),
            self.tiebacks.evaluate(ctx),
            self.monitoring.evaluate(ctx),
            self.dewatering.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("excavation-stage-gate", ctx, gates, {
            "GO": "Excavation stage clear.",
            "HOLD": "Excavation stage holding.",
            "ABORT": "Excavation stage aborted — secure face.",
        })

    def strut_waler_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "bracing": {**(ctx.get("bracing") or {}), "required": True}}
        gates = [
            self.bracing.evaluate(ctx),
            self.loads.evaluate(ctx),
            self.monitoring.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("strut-waler-gate", ctx, gates, {
            "GO": "Strut/waler clear.",
            "HOLD": "Strut/waler holding.",
            "ABORT": "Strut/waler aborted.",
        })

    def tieback_test_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "tiebacks": {**(ctx.get("tiebacks") or {}), "required": True}}
        gates = [
            self.tiebacks.evaluate(ctx),
            self.loads.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
            self.safety.evaluate(ctx),
        ]
        return self._finish("tieback-test-gate", ctx, gates, {
            "GO": "Tieback testing clear.",
            "HOLD": "Tieback testing holding.",
            "ABORT": "Tieback testing aborted.",
        })

    def monitoring_alarm_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.monitoring.evaluate(ctx),
            self.loads.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("monitoring-alarm-gate", ctx, gates, {
            "GO": "Monitoring within limits.",
            "HOLD": "Monitoring alert — eng review.",
            "ABORT": "Monitoring alarm — stop work.",
        })

    def dewatering_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.dewatering.evaluate(ctx),
            self.excavation.evaluate(ctx),
            self.weather.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("dewatering-gate", ctx, gates, {
            "GO": "Dewatering clear.",
            "HOLD": "Dewatering holding.",
            "ABORT": "Dewatering aborted.",
        })

    def brace_release_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "release": {**(ctx.get("release") or {}), "required": True}}
        gates = [
            self.release.evaluate(ctx),
            self.monitoring.evaluate(ctx),
            self.loads.evaluate(ctx),
            self.safety.evaluate(ctx),
            self.qa.evaluate(ctx, phase="during"),
        ]
        return self._finish("brace-release-gate", ctx, gates, {
            "GO": "Brace release sequence clear.",
            "HOLD": "Brace release holding.",
            "ABORT": "Brace release aborted.",
        })

    def weather_protect_gate(self, ctx: dict[str, Any]) -> SwarmResult:
        gates = [
            self.weather.evaluate(ctx),
            self.dewatering.evaluate(ctx),
            self.safety.evaluate(ctx),
        ]
        return self._finish("weather-protect-gate", ctx, gates, {
            "GO": "Weather/protection clear.",
            "HOLD": "Weather holding.",
            "ABORT": "Weather aborted.",
        })

    def soe_closeout(self, ctx: dict[str, Any]) -> SwarmResult:
        ctx = {**ctx, "release": {**(ctx.get("release") or {}), "required": True}}
        gates = [
            self.qa.evaluate(ctx, phase="closeout"),
            self.monitoring.evaluate(ctx),
            self.release.evaluate(ctx),
            self.loads.evaluate(ctx),
            self.crew.evaluate(ctx, require_briefing=False),
        ]
        return self._finish("soe-closeout", ctx, gates, {
            "GO": "SOE closeout clear.",
            "HOLD": "SOE closeout holding.",
            "ABORT": "SOE closeout aborted.",
        })

    def hold_abort(self, ctx: dict[str, Any]) -> SwarmResult:
        severity = str(ctx.get("severity") or "HOLD").upper()
        decision: Decision = "ABORT" if severity == "ABORT" else "HOLD"
        reason = ctx.get("block_reason") or "Escalated hold/abort"
        gates = [GateResult(
            "soe-lead",
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

    write(mod / "swarm.py", '''"""SOE / shoring swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.soe_swarm.schemas import SwarmResult
from modules.soe_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class SoeSwarm:
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
        log_event(f"[soe-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[soe-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result


__all__ = ["SoeSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "__init__.py", '''from modules.soe_swarm.swarm import SoeSwarm, SwarmResult
from modules.soe_swarm.workflows import WORKFLOW_IDS

__all__ = ["SoeSwarm", "SwarmResult", "WORKFLOW_IDS"]
''')
    write(mod / "cli.py", '''"""CLI for SOE / shoring swarm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.soe_swarm.swarm import SoeSwarm

app = typer.Typer(add_completion=False, help="SOE / shoring field swarm")


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
    for w in SoeSwarm().list_workflows():
        print(f"- {w}")


@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = SoeSwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "soe" / "fixtures" / "pre_soe_go.yaml"
    result = SoeSwarm().run("pre-soe-gate", yaml.safe_load(fixture.read_text()))
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

from modules.soe_swarm.swarm import SoeSwarm
from modules.soe_swarm.workflows import WORKFLOW_IDS


class Handler(BaseHTTPRequestHandler):
    swarm = SoeSwarm()

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[soe-swarm-api] {self.address_string()} {fmt % args}")

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
        if isinstance(payload.get("SoeContextJson"), str):
            try:
                context = {**context, **json.loads(payload["SoeContextJson"])}
            except json.JSONDecodeError:
                self._send(400, {"error": "SoeContextJson is not valid JSON"})
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
    p.add_argument("--port", type=int, default=8090)
    args = p.parse_args()
    print(f"SOE shoring swarm API on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
''')

    go = """zone_id: DEMO-BASEMENT-NORTH
area: Basement SOE Wall North
design:
  pe_stamped_approved: true
  products_approved: true
  monitoring_plan_approved: true
monitoring:
  baseline_set: true
  readings_current: true
  alarm_exceeded: false
  alert_exceeded: false
soldier_piles:
  required: true
  tip_ok: true
  plumb_ok: true
lagging:
  required: true
  installed_ok: true
  exposed_face_over_limit: false
  gaps_unpacked: false
sheet_pile:
  required: false
bracing:
  required: true
  missing_for_stage: false
  connections_ok: true
  preload_ok: true
tiebacks:
  required: true
  required_for_stage: true
  locked_off: true
  proof_test_pass: true
  grout_records_ok: true
excavation:
  current_depth_ft: 12
  allowed_depth_ft: 14
  prior_braces_incomplete: false
  spoil_at_crest: false
  continuing_after_alarm: false
dewatering:
  required: true
  system_running: true
  uncontrolled_inflow: false
  drawdown_ok: true
loads:
  required: true
  cells_active: true
  overload: false
release:
  required: true
  permanent_structure_ready: true
  sequence_ok: true
  monitoring_during: true
weather:
  storm_flood_risk: false
  sumps_protected: true
  freeze_thaw: false
  face_protected: true
  crest_surcharge: false
crew:
  roles:
    - soe_lead
    - pile_op
    - excavator_op
    - welder_fitter
    - anchor_crew
    - qc_tech
    - safety_watch
  headcount: 10
  briefing_complete: true
  fatigued_workers: []
qa:
  pre_hold_points_clear: true
  install_hold_points_clear: true
edge:
  unprotected: false
face:
  collapse_indicators: false
utilities:
  utility_strike: false
safety:
  violations: []
"""
    write(agents_root / "fixtures" / "pre_soe_go.yaml", go)
    write(studio / "samples" / "pre_soe_go.yaml", go)
    write(agents_root / "fixtures" / "over_excavate_abort.yaml", """zone_id: DEMO-BASEMENT-NORTH
excavation:
  current_depth_ft: 18
  allowed_depth_ft: 14
  prior_braces_incomplete: true
bracing:
  required: true
  missing_for_stage: true
  connections_ok: false
tiebacks:
  required: true
  required_for_stage: true
  locked_off: false
monitoring:
  baseline_set: true
  readings_current: true
  alarm_exceeded: false
dewatering:
  required: true
  system_running: true
  drawdown_ok: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "monitoring_alarm_abort.yaml", """zone_id: DEMO-BASEMENT-NORTH
monitoring:
  baseline_set: true
  readings_current: true
  alarm_exceeded: true
  alert_exceeded: true
loads:
  required: true
  cells_active: true
  overload: true
excavation:
  continuing_after_alarm: true
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "tieback_fail_hold.yaml", """zone_id: DEMO-BASEMENT-NORTH
tiebacks:
  required: true
  proof_test_pass: false
  grout_records_ok: true
  locked_off: false
loads:
  required: true
  cells_active: true
  overload: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "premature_release_abort.yaml", """zone_id: DEMO-BASEMENT-NORTH
release:
  required: true
  permanent_structure_ready: false
  sequence_ok: false
  monitoring_during: false
monitoring:
  baseline_set: true
  readings_current: true
  alarm_exceeded: false
loads:
  required: true
  cells_active: true
  overload: false
qa:
  install_hold_points_clear: true
safety:
  violations: []
""")
    write(agents_root / "fixtures" / "design_missing_hold.yaml", """zone_id: DEMO-BASEMENT-NORTH
design:
  pe_stamped_approved: false
  products_approved: false
  monitoring_plan_approved: false
monitoring:
  baseline_set: false
  readings_current: false
weather:
  storm_flood_risk: false
crew:
  roles: [soe_lead, pile_op, excavator_op, welder_fitter, anchor_crew, qc_tech, safety_watch]
  briefing_complete: true
qa:
  pre_hold_points_clear: true
safety:
  violations: []
""")

    write(ROOT / "tests" / "test_soe_swarm.py", '''from __future__ import annotations

from pathlib import Path
import yaml
from modules.soe_swarm.swarm import SoeSwarm
from modules.soe_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "soe" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(SoeSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_soe_go():
    assert SoeSwarm().run("pre-soe-gate", _load("pre_soe_go.yaml")).decision == "GO"


def test_over_excavate_abort():
    assert SoeSwarm().run("excavation-stage-gate", _load("over_excavate_abort.yaml")).decision == "ABORT"


def test_monitoring_alarm_abort():
    assert SoeSwarm().run("monitoring-alarm-gate", _load("monitoring_alarm_abort.yaml")).decision == "ABORT"


def test_tieback_fail_hold():
    assert SoeSwarm().run("tieback-test-gate", _load("tieback_fail_hold.yaml")).decision == "HOLD"


def test_premature_release_abort():
    assert SoeSwarm().run("brace-release-gate", _load("premature_release_abort.yaml")).decision == "ABORT"


def test_design_missing_hold():
    assert SoeSwarm().run("pre-soe-gate", _load("design_missing_hold.yaml")).decision == "HOLD"


def test_stage_go():
    assert SoeSwarm().run("excavation-stage-gate", _load("pre_soe_go.yaml")).decision == "GO"


def test_closeout_go():
    assert SoeSwarm().run("soe-closeout", _load("pre_soe_go.yaml")).decision == "GO"


def test_hold_abort():
    assert SoeSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "collapse"}).decision == "ABORT"
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

### SOE / Shoring Swarm (Copilot Studio)

Same pattern — field GO/HOLD/ABORT for support of excavation:

- [`copilot-studio/soe-crew/`](copilot-studio/soe-crew/) — parent + 16 child agents; open `START_HERE.md`
- Drop-in zip: [`packages/SoeShoring-Swarm-CopilotStudio-DropIn.zip`](packages/SoeShoring-Swarm-CopilotStudio-DropIn.zip)

```bash
python -m modules.soe_swarm.api --port 8090
python -m modules.soe_swarm.cli run pre-soe-gate -c agents/soe/fixtures/pre_soe_go.yaml
```
"""
        if "SOE / Shoring Swarm" not in rtxt and marker in rtxt:
            readme.write_text(rtxt.replace(marker, block + "\n", 1))

    packages = ROOT / "packages"
    packages.mkdir(exist_ok=True)
    zip_path = packages / "SoeShoring-Swarm-CopilotStudio-DropIn.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(studio.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                zf.write(path, path.relative_to(studio).as_posix())
    print(f"Wrote {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
