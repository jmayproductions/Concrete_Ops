# START HERE — Interiors Drywall Swarm drop-in

Ready Copilot Studio workspace for interiors / drywall / shafts field gates.

## 3 steps
1. Open this `interiors-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Interiors Drywall Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-interiors-gate…”*.

## Workflows
`pre-interiors-gate`, `layout-framing-gate`, `metal-stud-runbook`, `shaftwall-gate`, `fire-rated-assembly-gate`, `acoustics-stc-gate`, `inwall-cover-release`, `board-hang-runbook`, `taping-finish-gate`, `weather-protect-gate`, `interiors-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.interiors_swarm.api --port 8091
python -m modules.interiors_swarm.cli run pre-interiors-gate -c agents/interiors/fixtures/pre_interiors_go.yaml
```
