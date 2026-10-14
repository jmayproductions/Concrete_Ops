# START HERE — Life Safety + Door Hardware Swarm drop-in

Ready Copilot Studio workspace for egress, fire doors, sprinklers/alarm, and TCO prep gates.

## 3 steps
1. Open this `life-safety-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Life Safety Door Hardware Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-ls-gate…”*.

## Workflows
`pre-ls-gate`, `egress-path-gate`, `exit-signage-gate`, `egress-lighting-gate`, `door-hardware-gate`, `fire-door-gate`, `sprinkler-hydro-gate`, `fire-alarm-gate`, `smoke-damper-gate`, `punch-walk-gate`, `tco-readiness`, `hold-abort`

## Optional backend
```bash
python -m modules.life_safety_swarm.api --port 8103
python -m modules.life_safety_swarm.cli run pre-ls-gate -c agents/life-safety/fixtures/pre_ls_go.yaml
```
