# START HERE — FormSure Formwork Swarm drop-in

Ready Copilot Studio workspace for formwork erect / pour / strip field gates.

## 3 steps
1. Open this `formsure-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **FormSure Formwork Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-pour-form-gate…”*.

## Workflows
`pre-pour-form-gate`, `form-erect-gate`, `release-agent-check`, `tie-brace-gate`, `scc-leak-gate`, `pour-drop-gate`, `form-pressure-gate`, `shore-stability-gate`, `strip-readiness-gate`, `load-transfer-gate`, `post-strip-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.formsure_swarm.api --port 8097
python -m modules.formsure_swarm.cli run pre-pour-form-gate -c agents/formsure/fixtures/pre_pour_go.yaml
```
