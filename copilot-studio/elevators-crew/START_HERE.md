# START HERE — Elevators VTR Swarm drop-in

Ready Copilot Studio workspace for elevator / vertical transportation field gates.

## 3 steps
1. Open this `elevators-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Elevators VTR Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-elevator-gate…”*.

## Workflows
`pre-elevator-gate`, `pit-machine-room-gate`, `rail-install-runbook`, `hoistway-clearance-gate`, `door-entrance-gate`, `cab-controller-gate`, `safety-devices-gate`, `temporary-run-gate`, `ahj-inspection-gate`, `weather-protect-gate`, `elevator-turnover`, `hold-abort`

## Optional backend
```bash
python -m modules.elevators_swarm.api --port 8092
python -m modules.elevators_swarm.cli run pre-elevator-gate -c agents/elevators/fixtures/pre_elevator_go.yaml
```
