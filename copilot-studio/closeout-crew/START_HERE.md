# START HERE — Closeout Turnover Swarm drop-in

Ready Copilot Studio workspace for punch / TCO / turnover gates.

## 3 steps
1. Open this `closeout-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Closeout Turnover Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-closeout-gate…”*.

## Workflows
`pre-closeout-gate`, `room-readiness-gate`, `punchlist-walk`, `life-safety-gate`, `door-hardware-qa`, `finishes-punch-gate`, `fire-protection-closeout`, `commissioning-gate`, `ncr-closeout-gate`, `tco-readiness-gate`, `turnover-package-gate`, `hold-abort`

## Optional backend
```bash
python -m modules.closeout_swarm.api --port 8087
python -m modules.closeout_swarm.cli run pre-closeout-gate -c agents/closeout/fixtures/pre_closeout_go.yaml
```
