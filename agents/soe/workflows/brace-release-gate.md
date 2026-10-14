# Workflow: `brace-release-gate`

Gate order:
1. `brace-release`
2. `survey-monitoring`
3. `load-monitoring`
4. `safety-failsafe`
5. `qa-inspector`

SafetyFailsafe FAIL => ABORT.
