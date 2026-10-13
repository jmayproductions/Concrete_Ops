# ConcreteOps Crew Swarm — Microsoft Copilot Studio work environment

This folder is the **primary** authoring pack for the concrete master stack.
Open it with the **Copilot Studio VS Code extension** (or clone into your
Copilot Studio work environment) and push to your Power Platform environment.

Docker Agent YAML under `agents/concrete-crew/` remains a reference twin.
The deterministic Python swarm under `modules/agent_swarm/` is the **tool backend**
Studio should call for repeatable GO/HOLD/ABORT.

## Folder map (MCS)

```
concrete-crew/
  agent.mcs.yml              # Parent orchestrator
  settings.mcs.yml           # Generative orchestration ON
  agents/<Name>/agent.mcs.yml  # 14 child agents (AgentDialog)
  knowledge/specialists/     # Instruction playbooks (upload after push)
  knowledge/workflows/       # Gate-order playbooks
  actions/RunDeterministicWorkflow.mcs.yml
  topics/                    # Optional AdaptiveDialog starters
```

## Bring-up in the Studio work environment

1. **Install / open** the Copilot Studio extension in VS Code and sign into the
   target Power Platform environment (Dev recommended first).
2. **Clone / open** this `copilot-studio/concrete-crew` directory as the agent root
   (must contain `agent.mcs.yml` + `settings.mcs.yml`).
3. **Push** the parent agent to the environment (extension: push / sync).
4. **Push child agents** under `agents/*` (Phase 1 — plain AgentDialog only).
   Do **not** attach knowledge until children exist in the environment.
5. After children are visible in Studio UI, **add knowledge sources** from
   `knowledge/specialists` and `knowledge/workflows` (Phase 2).
6. Confirm **Generative orchestration** is enabled (`settings.mcs.yml`).
7. Wire **RunDeterministicWorkflow** to Power Automate or a custom connector
   pointing at the swarm HTTP API (below).
8. Test conversation starters: pre-pour, PT stress, tilt lift, strip/reshore,
   mass thermal, curing release.

## Multi-agent pattern used

| Studio concept | ConcreteOps mapping |
| --- | --- |
| Parent agent | Crew Swarm coordinator |
| Child agents (`AgentDialog`) | PourLead, CrewOps, QcInspector, WeatherGate, SafetyFailsafe, MaterialsMix, PtStress, TiltUp, Sog, Shotcrete, CipWall, ElevatedDeck, MassThermal, CuringLifecycle |
| Knowledge | Workflow gate-order + specialist SOPs |
| Tool / action | Deterministic swarm HTTP twin |
| Channels | Teams / custom website / Power Apps (configure in Studio) |

Parent instructions force: invoke children in playbook order → wait → combine →
one user reply. Children return structured `Decision` / `Summary` / `GatesJson` /
`ActionsJson` and **must not** reply to the field user directly.

## Deterministic backend (Power Automate / connector)

Run the twin locally or on Azure:

```bash
PYTHONPATH=. python -m modules.agent_swarm.api --host 0.0.0.0 --port 8080
```

| Method | Path | Body |
| --- | --- | --- |
| `GET` | `/v1/workflows` | — |
| `POST` | `/v1/workflows/{id}/run` | `{ "context": { ... } }` |

Response matches Studio output shape:

```json
{
  "workflow": "pre-pour-gate",
  "pour_id": "L4-DECK-A",
  "decision": "GO",
  "summary": "...",
  "gates": [...],
  "actions": [...]
}
```

In Power Automate: **HTTP** action → map `WorkflowId` + `PourContextJson` →
return `decision` / `summary` to the agent tool.

## Auth / data

- Prefer **Integrated** auth for internal StructureWave tenants.
- Store pour tickets / telemetry in Dataverse or SharePoint lists; pass a
  `PourContextJson` snapshot into the parent (do not put secrets in instructions).
- Keep provider keys and plant credentials in Azure Key Vault / environment
  variables — never in `settings.instructions`.

## Solution export

When stable, pack parent + children + knowledge + connector reference into a
**Power Platform solution** (or Component collection) and export managed ZIP
for QA/Prod environments.
