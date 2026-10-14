# START HERE — Precast Panelized Swarm drop-in

Ready Copilot Studio workspace for precast / panelized erection.

## 3 steps
1. Open this `precast-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Precast Panelized Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-erect-gate…”*.

## Workflows
`pre-erect-gate`, `fab-release-gate`, `delivery-panel-gate`, `lift-day-runbook`, `panel-set-qa`, `bracing-lock`, `connection-grout-qa`, `brace-release-gate`, `hybrid-interface-gate`, `level-closeout`, `weather-lift-hold`, `hold-abort`

## Optional backend
```bash
python -m modules.precast_swarm.api --port 8085
python -m modules.precast_swarm.cli run pre-erect-gate -c agents/precast/fixtures/pre_erect_go.yaml
```
