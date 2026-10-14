# START HERE — Earthwork Swarm drop-in

Ready Copilot Studio workspace for earthwork / site civil field gates.

## 3 steps
1. Open this `earthwork-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Earthwork Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-earthwork-gate…”*.

## Workflows
`pre-earthwork-gate`, `utilities-locate-gate`, `excavation-runbook`, `subgrade-accept-gate`, `compaction-lift-runbook`, `trench-backfill-gate`, `drainage-swale-qa`, `erosion-control-gate`, `paving-prep-gate`, `weather-protect-gate`, `earthwork-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.earthwork_swarm.api --port 8088
python -m modules.earthwork_swarm.cli run pre-earthwork-gate -c agents/earthwork/fixtures/pre_earthwork_go.yaml
```
