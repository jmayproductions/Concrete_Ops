# Workflow: `monitoring-alarm-gate`

Gate order:
1. `survey-monitoring`
2. `load-monitoring`
3. `safety-failsafe`
4. `qa-inspector`

SafetyFailsafe FAIL => ABORT.
