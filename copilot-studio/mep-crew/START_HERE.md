# START HERE — MEP Firestop Swarm drop-in

Ready Copilot Studio workspace for MEP rough-in and firestop.

## 3 steps
1. Open this `mep-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **MEP Firestop Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-mep-gate…”*.

## Workflows
`pre-mep-gate`, `clash-sleeve-gate`, `hvac-rough-runbook`, `electrical-rough-runbook`, `plumbing-rough-runbook`, `firestop-precover-gate`, `damper-life-safety-gate`, `shaft-inspection-gate`, `pressure-test-gate`, `inwall-cover-release`, `mep-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.mep_swarm.api --port 8084
python -m modules.mep_swarm.cli run pre-mep-gate -c agents/mep/fixtures/pre_mep_go.yaml
```
