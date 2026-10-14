# START HERE — Heavy Lift Crane Swarm drop-in

Ready Copilot Studio workspace for heavy-lift / crane day field gates.

## 3 steps
1. Open this `heavy-lift-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Heavy Lift Crane Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-lift-gate…”*.

## Workflows
`pre-lift-gate`, `lift-plan-review`, `ground-bearing-gate`, `rigging-inspection`, `load-chart-gate`, `power-line-clearance`, `exclusion-zone-gate`, `critical-lift-runbook`, `tandem-lift-gate`, `weather-wind-gate`, `post-lift-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.heavy_lift_swarm.api --port 8096
python -m modules.heavy_lift_swarm.cli run pre-lift-gate -c agents/heavy-lift/fixtures/pre_lift_go.yaml
```
