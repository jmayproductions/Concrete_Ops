# START HERE — Roofing QAQC Swarm drop-in

Ready Copilot Studio workspace for steep-slope and flat roofing field gates.

## 3 steps
1. Open this `roofing-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Roofing QAQC Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-roof-gate…”*.

## Workflows
`pre-roof-gate`, `deck-prep-gate`, `underlayment-gate`, `fastener-gate`, `shingle-course-gate`, `flashing-gate`, `valley-penetration-gate`, `membrane-flat-gate`, `high-wind-gate`, `ridge-closeout`, `final-inspection`, `hold-abort`

## Optional backend
```bash
python -m modules.roofing_swarm.api --port 8100
python -m modules.roofing_swarm.cli run pre-roof-gate -c agents/roofing/fixtures/pre_roof_go.yaml
```
