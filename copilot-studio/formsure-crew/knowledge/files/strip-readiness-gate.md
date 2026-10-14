# Workflow: `strip-readiness-gate`

Gate order:
1. `strip-timing`
2. `load-transfer`
3. `shoring-props`
4. `safety-failsafe`
5. `qa-inspector`

SafetyFailsafe FAIL => ABORT.
