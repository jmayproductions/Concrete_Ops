# ConcreteOps Crew Swarm (Copilot Studio)

**Primary runtime:** Microsoft Copilot Studio work environment.

| Artifact | Role |
| --- | --- |
| `agent.mcs.yml` | Parent orchestrator |
| `settings.mcs.yml` | Generative orchestration enabled |
| `agents/*/agent.mcs.yml` | 14 child specialists (`AgentDialog`) |
| `knowledge/` | SOP + gate-order playbooks (attach after push) |
| `actions/RunDeterministicWorkflow.mcs.yml` | Hook for Python swarm twin |
| `STUDIO-WORK-ENVIRONMENT.md` | Step-by-step bring-up |

## Quick start

1. Open this folder in VS Code with the Copilot Studio extension.
2. Push parent, then child agents, then knowledge (see work-environment guide).
3. Optional backend: `python -m modules.agent_swarm.api`

## Related

- Deterministic twin: `modules/agent_swarm/`
- Legacy Docker Agent reference: `agents/concrete-crew/agent.yaml`
