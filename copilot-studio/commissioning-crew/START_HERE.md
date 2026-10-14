# START HERE — Commissioning Swarm drop-in

Ready Copilot Studio workspace for Cx plan → TAB → functional → closeout field gates.

## 3 steps
1. Open this `commissioning-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Commissioning Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-cx-gate…”*.

## Workflows
`pre-cx-gate`, `prefunctional-gate`, `startup-gate`, `tab-gate`, `functional-test-gate`, `witness-signoff-gate`, `performance-gate`, `calibration-gate`, `life-safety-cx-gate`, `om-training-gate`, `cx-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.commissioning_swarm.api --port 8102
python -m modules.commissioning_swarm.cli run pre-cx-gate -c agents/commissioning/fixtures/pre_cx_go.yaml
```
