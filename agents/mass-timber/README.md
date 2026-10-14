# Mass Timber Sequencing Swarm (reference twin)

> **Primary runtime is Microsoft Copilot Studio.**  
> See [`../../copilot-studio/mass-timber-crew/`](../../copilot-studio/mass-timber-crew/) and open `START_HERE.md` there.

This folder keeps:

- Specialist SOPs (`instructions/`) + gate-order playbooks (`workflows/`)
- YAML fixtures for the deterministic Python twin (`modules/mass_timber_swarm`)
- Source citations (`SOURCES.md`) from Scarlett 220310 + MTM 033021

## Coverage (successful engineered wood erection)

| Area | Specialist / workflow |
| --- | --- |
| Shops / CNC / JIT delivery | supply-chain, delivery-jit-gate |
| Survey / embeds / podium | survey-tolerance, hybrid-interface-gate |
| Crane / trailer-direct | crane-logistics |
| Moisture management | moisture-protect, moisture-daily-check |
| Temp bracing / diaphragm | temp-bracing, bracing-diaphragm-lock |
| CLT/NLT/DLT/MPP panels | panel-erect, panel-placement |
| Glulam frame | glulam-frame, glulam-frame-erect |
| Connections / hardware | connections, connection-qa |
| Fire / acoustic / MEP | assembly-systems |
| Exposed finish protection | finish-protect |
| Weather / safety | weather-gate, safety-failsafe |
| Level sequence / closeout | erect-lead, level-erect-runbook, level-closeout, topping-release |

## Deterministic twin (Studio tool backend)

```bash
python -m modules.mass_timber_swarm.cli list
python -m modules.mass_timber_swarm.cli run pre-erect-gate -c agents/mass-timber/fixtures/pre_erect_go.yaml
python -m modules.mass_timber_swarm.api --port 8081
```

Copilot Studio / Power Automate should `POST /v1/workflows/{id}/run` with erect context JSON.
