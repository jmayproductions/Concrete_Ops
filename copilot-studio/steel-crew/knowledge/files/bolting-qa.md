# Workflow: `bolting-qa`

Gate order:
1. `bolting`
2. `qa-inspector`
3. `safety-failsafe`

Parent assembles Decision from gates. SafetyFailsafe FAIL => ABORT.
