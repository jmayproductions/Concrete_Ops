# START HERE — Deep Foundations Swarm drop-in

Ready Copilot Studio workspace for deep foundation field gates.

## 3 steps
1. Open this `deep-foundations-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Deep Foundations Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-foundation-gate…”*.

## Workflows
`pre-foundation-gate`, `layout-stake-gate`, `drilled-shaft-runbook`, `tip-elevation-gate`, `cage-placement-gate`, `tremie-pour-runbook`, `driven-pile-runbook`, `integrity-test-gate`, `capacity-accept-gate`, `weather-protect-gate`, `foundations-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.deep_foundations_swarm.api --port 8089
python -m modules.deep_foundations_swarm.cli run pre-foundation-gate -c agents/deep-foundations/fixtures/pre_foundation_go.yaml
```
