# START HERE — SOE Shoring Swarm drop-in

Ready Copilot Studio workspace for support-of-excavation field gates.

## 3 steps
1. Open this `soe-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **SOE Shoring Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-soe-gate…”*.

## Workflows
`pre-soe-gate`, `pile-install-runbook`, `lagging-install-gate`, `excavation-stage-gate`, `strut-waler-gate`, `tieback-test-gate`, `monitoring-alarm-gate`, `dewatering-gate`, `brace-release-gate`, `weather-protect-gate`, `soe-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.soe_swarm.api --port 8090
python -m modules.soe_swarm.cli run pre-soe-gate -c agents/soe/fixtures/pre_soe_go.yaml
```
