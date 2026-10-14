"""Precast / panelized swarm coordinator."""

from __future__ import annotations

from typing import Any

from modules.precast_swarm.schemas import SwarmResult
from modules.precast_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event


class PrecastSwarm:
    def __init__(self, runner: WorkflowRunner | None = None) -> None:
        self.runner = runner or WorkflowRunner()
        self.handlers = get_workflow_handlers(self.runner)

    def list_workflows(self) -> list[str]:
        return list(WORKFLOW_IDS)

    def run(self, workflow: str, context: dict[str, Any] | None = None) -> SwarmResult:
        if workflow not in self.handlers:
            raise ValueError(f"Unknown workflow '{workflow}'. Known: {', '.join(WORKFLOW_IDS)}")
        ctx = dict(context or {})
        ctx.setdefault("erect_id", "ERECT-UNSET")
        log_event(f"[precast-swarm] starting workflow={workflow} erect={ctx['erect_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[precast-swarm] finished workflow={result.workflow} erect={result.erect_id} decision={result.decision}")
        return result


__all__ = ["PrecastSwarm", "SwarmResult", "WORKFLOW_IDS"]
