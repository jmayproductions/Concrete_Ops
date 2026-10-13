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
| `pt-stress` | Post-tension strength gate, stressing sequence, elongation, cert |
| `tilt-up` | Panel cast, cure-to-lift, erect day, brace & release |

## Named workflows

| Command | Workflow id | Purpose |
| --- | --- | --- |
| `/pre-pour` | `pre-pour-gate` | Mix → weather → QC → crew → failsafe → pour lead |
| `/pour-day` | `pour-day-runbook` | Placement execution with watches |
| `/mid-pour` | `mid-pour-monitor` | Fast health check while pouring |
| `/closeout` | `post-pour-closeout` | Closeout packet + curing owner |
| `/briefing` | `crew-briefing` | Six-item morning briefing |
| `/hold-abort` | `hold-abort` | Standard HOLD/ABORT escalation |
| `/pt-pre-stress` | `pt-pre-stress-gate` | Strength + tendon inventory before jacks |
| `/pt-stress` | `pt-stress-sequence` | Stressing order, elongation, inspection/cert |
| `/tilt-cast` | `tilt-up-cast-gate` | Panel bed cast readiness (embeds/plates) |
| `/tilt-lift` | `tilt-up-lift-day` | Erect day — wind, crane, braces before release |
| `/tilt-brace` | `tilt-up-brace-release` | Temporary brace removal gate |

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
python -m modules.agent_swarm.cli run pt-pre-stress-gate -c agents/concrete-crew/fixtures/pt_pre_stress_go.yaml
python -m modules.agent_swarm.cli run pt-stress-sequence -c agents/concrete-crew/fixtures/pt_elongation_hold.yaml
python -m modules.agent_swarm.cli run tilt-up-cast-gate -c agents/concrete-crew/fixtures/tilt_cast_go.yaml
python -m modules.agent_swarm.cli run tilt-up-lift-day -c agents/concrete-crew/fixtures/tilt_lift_wind_hold.yaml
```

Exit code `0` = GO, `2` = HOLD/ABORT.
