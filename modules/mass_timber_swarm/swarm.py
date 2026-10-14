"""Mass timber sequencing swarm coordinator — routes named workflows to gates."""

from __future__ import annotations

from typing import Any

from modules.mass_timber_swarm.schemas import SwarmResult
from modules.mass_timber_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class TimberSwarm:
    """Deterministic swarm twin for Copilot Studio mass timber erection."""

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
        ctx.setdefault("erect_id", "ERECT-UNSET")
        log_event(f"[timber-swarm] starting workflow={workflow} erect={ctx['erect_id']}")
        result = self.handlers[workflow](ctx)
        log_event(
            f"[timber-swarm] finished workflow={result.workflow} "
            f"erect={result.erect_id} decision={result.decision}"
        )
        return result


__all__ = ["TimberSwarm", "SwarmResult", "WORKFLOW_IDS"]
