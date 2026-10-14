# START HERE — Daily Safety Swarm drop-in

Ready Copilot Studio workspace for daily safety / hot work / confined space gates.

## 3 steps
1. Open this `daily-safety-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Daily Safety Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-shift-safety-gate…”*.

## Workflows
`pre-shift-safety-gate`, `hot-work-permit-gate`, `confined-space-entry`, `loto-release-gate`, `fall-protection-gate`, `excavation-safety-gate`, `crane-exclusion-gate`, `fire-watch-closeout`, `incident-abort`, `weather-emergency-gate`, `end-of-shift-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.daily_safety_swarm.api --port 8095
python -m modules.daily_safety_swarm.cli run pre-shift-safety-gate -c agents/daily-safety/fixtures/pre_shift_go.yaml
```
