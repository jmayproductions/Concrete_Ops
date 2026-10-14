# START HERE — Survey Layout Swarm drop-in

Ready Copilot Studio workspace for survey / layout / control field gates.

## 3 steps
1. Open this `survey-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Survey Layout Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-survey-gate…”*.

## Workflows
`pre-survey-gate`, `control-network-gate`, `stakeout-runbook`, `embed-layout-gate`, `grade-check-gate`, `as-built-capture`, `tolerance-accept-gate`, `bim-layout-gate`, `calibration-gate`, `weather-protect-gate`, `survey-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.survey_swarm.api --port 8094
python -m modules.survey_swarm.cli run pre-survey-gate -c agents/survey/fixtures/pre_survey_go.yaml
```
