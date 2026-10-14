# Workflow: `fab-release-gate`

Gate order:
1. `fab-release`
2. `qa-inspector`
3. `safety-failsafe`

SafetyFailsafe FAIL => ABORT.
