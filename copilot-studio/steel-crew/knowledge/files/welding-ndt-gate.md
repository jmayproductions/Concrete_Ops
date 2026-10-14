# Workflow: `welding-ndt-gate`

Gate order:
1. `welding`
2. `qa-inspector`
3. `weather-gate`
4. `safety-failsafe`

Parent assembles Decision from gates. SafetyFailsafe FAIL => ABORT.
