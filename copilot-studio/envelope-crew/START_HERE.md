# START HERE — Envelope Waterproofing Swarm drop-in

Ready Copilot Studio workspace for field envelope / waterproofing.

## 3 steps
1. Open this `envelope-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Envelope Waterproofing Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-envelope-gate…”*.

## Workflows
`pre-envelope-gate`, `substrate-ready-gate`, `wrb-air-barrier-gate`, `below-grade-wp-runbook`, `roofing-membrane-runbook`, `flashing-penetration-qa`, `curtain-wall-install-gate`, `cladding-rainscreen-gate`, `water-test-gate`, `air-barrier-test-gate`, `envelope-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.envelope_swarm.api --port 8083
python -m modules.envelope_swarm.cli run pre-envelope-gate -c agents/envelope/fixtures/pre_envelope_go.yaml
```
