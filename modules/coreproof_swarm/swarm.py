"""CoreProof lab swarm coordinator."""
from __future__ import annotations
from typing import Any
from modules.coreproof_swarm.schemas import SwarmResult
from modules.coreproof_swarm.workflows import WORKFLOW_IDS, WorkflowRunner, get_workflow_handlers
from shared.utils import log_event

class CoreProofSwarm:
    def __init__(self, runner: WorkflowRunner | None = None) -> None:
        self.runner = runner or WorkflowRunner()
        self.handlers = get_workflow_handlers(self.runner)
    def list_workflows(self) -> list[str]:
        return list(WORKFLOW_IDS)
    def run(self, workflow: str, context: dict[str, Any] | None = None) -> SwarmResult:
        if workflow not in self.handlers:
            raise ValueError(f"Unknown workflow '{workflow}'. Known: {', '.join(WORKFLOW_IDS)}")
        ctx = dict(context or {}); ctx.setdefault("zone_id", "ZONE-UNSET")
        log_event(f"[coreproof-swarm] starting workflow={workflow} zone={ctx['zone_id']}")
        result = self.handlers[workflow](ctx)
        log_event(f"[coreproof-swarm] finished workflow={result.workflow} zone={result.zone_id} decision={result.decision}")
        return result

__all__ = ["CoreProofSwarm", "SwarmResult", "WORKFLOW_IDS"]
