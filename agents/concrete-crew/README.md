# ConcreteOps™ Crew Swarm

Multi-agent swarm for **perfect, repeatable concrete crew workflows**.

## Agents

| Agent | Role |
| --- | --- |
| `root` | Coordinator — routes named workflows, returns GO / HOLD / ABORT |
| `pour-lead` | Pour lifecycle + placement plan |
| `crew-ops` | Manning, fatigue, briefing script |
| `qc-inspector` | Pre / during / post QC gates |
| `weather-gate` | Weather holds + hot/cold/rain/wind protocols |
| `safety-failsafe` | Stop-work authority (FAIL → ABORT) |
| `materials-mix` | Mix ticket + delivery cadence |

## Named workflows

| Command | Workflow id | Purpose |
| --- | --- | --- |
| `/pre-pour` | `pre-pour-gate` | Mix → weather → QC → crew → failsafe → pour lead |
| `/pour-day` | `pour-day-runbook` | Placement execution with watches |
| `/mid-pour` | `mid-pour-monitor` | Fast health check while pouring |
| `/closeout` | `post-pour-closeout` | Closeout packet + curing owner |
| `/briefing` | `crew-briefing` | Six-item morning briefing |
| `/hold-abort` | `hold-abort` | Standard HOLD/ABORT escalation |

Playbooks live in `workflows/`. Specialist prompts live in `instructions/`.

## Run with Docker Agent

```bash
docker agent debug config ./agents/concrete-crew/agent.yaml
docker agent debug toolsets ./agents/concrete-crew/agent.yaml
docker agent doctor ./agents/concrete-crew/agent.yaml
docker agent run ./agents/concrete-crew/agent.yaml
# then invoke a named command, e.g. /pre-pour
```

Provider keys come from the environment (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) or `docker agent setup`. Local fallback uses Docker Model Runner (`dmr`).

## Run deterministically (no LLM)

The same gate order ships as a Python swarm for CI and field sim:

```bash
python -m modules.agent_swarm.cli list
python -m modules.agent_swarm.cli demo
python -m modules.agent_swarm.cli run pre-pour-gate -c agents/concrete-crew/fixtures/pre_pour_go.yaml
python -m modules.agent_swarm.cli run pre-pour-gate -c agents/concrete-crew/fixtures/pre_pour_weather_hold.yaml
python -m modules.agent_swarm.cli run pour-day-runbook -c agents/concrete-crew/fixtures/failsafe_abort.yaml
```

Exit code `0` = GO, `2` = HOLD/ABORT.
