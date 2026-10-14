# START HERE — Masonry Swarm drop-in

Ready Copilot Studio workspace for masonry field gates.

## 3 steps
1. Open this `masonry-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Masonry Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-masonry-gate…”*.

## Workflows
`pre-masonry-gate`, `layout-coursing-gate`, `daily-layup-runbook`, `mortar-qc-check`, `rebar-pregrout-gate`, `grout-lift-runbook`, `flashing-weep-qa`, `plumb-tolerance-check`, `veneer-rainscreen-gate`, `weather-protect-gate`, `masonry-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.masonry_swarm.api --port 8086
python -m modules.masonry_swarm.cli run pre-masonry-gate -c agents/masonry/fixtures/pre_masonry_go.yaml
```
