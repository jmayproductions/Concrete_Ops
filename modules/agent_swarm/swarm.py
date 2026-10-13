"""Crew swarm coordinator — routes named workflows to specialist gates."""

from __future__ import annotations

from typing import Any

from modules.agent_swarm.schemas import SwarmResult
from modules.agent_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class CrewSwarm:
    """Deterministic swarm that mirrors agents/concrete-crew/agent.yaml workflows."""

    def __init__(self, runner: WorkflowRunner | None = None) -> None:
        self.runner = runner or WorkflowRunner()
        self.handlers = get_workflow_handlers(self.runner)

    def list_workflows(self) -> list[str]:
        return list(WORKFLOW_IDS)

    def run(self, workflow: str, context: dict[str, Any] | None = None) -> SwarmResult:
        if workflow not in self.handlers:
            known = ", ".join(WORKFLOW_IDS)
            raise ValueError(f"Unknown workflow '{workflow}'. Known: {known}")
        ctx = dict(context or {})
        ctx.setdefault("pour_id", "POUR-UNSET")
        log_event(f"[swarm] starting workflow={workflow} pour={ctx['pour_id']}")
        result = self.handlers[workflow](ctx)
        log_event(
            f"[swarm] finished workflow={result.workflow} pour={result.pour_id} decision={result.decision}"
        )
        return result


# Re-export for convenient imports
__all__ = ["CrewSwarm", "SwarmResult", "WORKFLOW_IDS"]
