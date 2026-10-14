# Workflow: `witness-signoff-gate`

Gate order:
1. `witness-signoff`
2. `functional-test`
3. `qa-inspector`
4. `safety-failsafe`

SafetyFailsafe FAIL => ABORT.
