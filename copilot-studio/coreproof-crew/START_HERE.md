# START HERE — CoreProof Lab Swarm drop-in

Ready Copilot Studio workspace for cylinder/core strength verification gates.

## 3 steps
1. Open this `coreproof-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **CoreProof Lab Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-sample-gate…”*.

## Workflows
`pre-sample-gate`, `cast-handling-gate`, `transport-lab-gate`, `moist-cure-gate`, `break-schedule-gate`, `cylinder-break-gate`, `core-test-gate`, `strength-compliance-gate`, `field-vs-lab-gate`, `low-strength-abort`, `lab-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.coreproof_swarm.api --port 8099
python -m modules.coreproof_swarm.cli run pre-sample-gate -c agents/coreproof/fixtures/pre_sample_go.yaml
```
