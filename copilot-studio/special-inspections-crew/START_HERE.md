# START HERE — Special Inspections Swarm drop-in

Ready Copilot Studio workspace for SI / hold-point coordination.

## 3 steps
1. Open this `special-inspections-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Special Inspections Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-si-program-gate…”*.

## Workflows
`pre-si-program-gate`, `daily-si-dispatch`, `soils-foundation-hold`, `concrete-pour-si-gate`, `steel-connection-si-gate`, `masonry-grout-si-gate`, `fireproofing-si-gate`, `ndt-release-gate`, `cover-before-si-gate`, `ncr-disposition-gate`, `si-final-report`, `hold-abort`

## Optional backend
```bash
python -m modules.special_inspections_swarm.api --port 8093
python -m modules.special_inspections_swarm.cli run pre-si-program-gate -c agents/special-inspections/fixtures/pre_si_go.yaml
```
