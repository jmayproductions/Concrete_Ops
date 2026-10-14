# Workflow: `critical-lift-runbook`

Gate order:
1. `lift-plan`
2. `load-chart`
3. `ground-bearing`
4. `rigging-gear`
5. `power-lines`
6. `exclusion-zone`
7. `signal-comms`
8. `weather-wind`
9. `safety-failsafe`
10. `qa-inspector`

SafetyFailsafe FAIL => ABORT.
