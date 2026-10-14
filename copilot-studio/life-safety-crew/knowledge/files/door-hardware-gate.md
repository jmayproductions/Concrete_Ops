# Workflow: `door-hardware-gate`

Gate order:
1. `door-schedule`
2. `door-hardware`
3. `fire-door`
4. `qa-inspector`
5. `safety-failsafe`

SafetyFailsafe FAIL => ABORT.
