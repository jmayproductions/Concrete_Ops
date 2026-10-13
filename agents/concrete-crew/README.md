# ConcreteOps Crew Swarm (reference twin)

> **Primary runtime is Microsoft Copilot Studio.**  
> See [`../../copilot-studio/concrete-crew/`](../../copilot-studio/concrete-crew/) and [`STUDIO-WORK-ENVIRONMENT.md`](../../copilot-studio/concrete-crew/STUDIO-WORK-ENVIRONMENT.md).

This folder keeps:

- Docker Agent `agent.yaml` (optional local multi-agent reference)
- Markdown playbooks + fixtures shared with Studio knowledge
- Inputs for the deterministic Python twin (`modules/agent_swarm`)

## Deterministic twin (Studio tool backend)

```bash
python -m modules.agent_swarm.cli list
python -m modules.agent_swarm.api --port 8080
```

Copilot Studio / Power Automate should `POST /v1/workflows/{id}/run` with pour context JSON.
