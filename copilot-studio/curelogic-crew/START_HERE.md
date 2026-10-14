# START HERE — CureLogic Curing Swarm drop-in

Ready Copilot Studio workspace for curing lifecycle field gates.

## 3 steps
1. Open this `curelogic-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **CureLogic Curing Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-cure-gate…”*.

## Workflows
`pre-cure-gate`, `evaporation-gate`, `thermal-envelope-gate`, `wet-cure-gate`, `membrane-cure-gate`, `cover-integrity-gate`, `cold-weather-cure-gate`, `hot-weather-cure-gate`, `steam-accel-gate`, `day-n-maturity-gate`, `curing-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.curelogic_swarm.api --port 8098
python -m modules.curelogic_swarm.cli run pre-cure-gate -c agents/curelogic/fixtures/pre_cure_go.yaml
```
