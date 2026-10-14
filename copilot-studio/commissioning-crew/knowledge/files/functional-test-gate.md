# Workflow: `functional-test-gate`

Gate order:
1. `functional-test`
2. `witness-signoff`
3. `performance-tol`
4. `safety-failsafe`
5. `qa-inspector`

SafetyFailsafe FAIL => ABORT.
