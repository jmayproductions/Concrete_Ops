# Workflow: `load-chart-gate`

Gate order:
1. `load-chart`
2. `lift-plan`
3. `qa-inspector`
4. `safety-failsafe`

SafetyFailsafe FAIL => ABORT.
