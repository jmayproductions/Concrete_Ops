from __future__ import annotations

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
    pour_id: str
    decision: Decision
    summary: str
    gates: list[GateResult]
    actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow,
            "pour_id": self.pour_id,
            "decision": self.decision,
            "summary": self.summary,
            "gates": [g.to_dict() for g in self.gates],
            "actions": list(self.actions),
        }

    def render(self) -> str:
        lines = [
            f"WORKFLOW: {self.workflow}",
            f"POUR: {self.pour_id}",
            f"DECISION: {self.decision}",
            f"SUMMARY: {self.summary}",
            "GATES:",
        ]
        for gate in self.gates:
            lines.append(f"- {gate.agent}: {gate.status} — {gate.detail}")
        lines.append("ACTIONS:")
        for action in self.actions:
            lines.append(f"- {action}")
        return "\n".join(lines)
