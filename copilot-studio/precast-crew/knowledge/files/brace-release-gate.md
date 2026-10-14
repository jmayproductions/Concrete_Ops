# Workflow: `brace-release-gate`

Gate order:
1. `brace-release`
2. `connections`
3. `temp-bracing`
4. `qa-inspector`
5. `safety-failsafe`

SafetyFailsafe FAIL => ABORT.
