# Workflow: `bracing-stability-lock`

Gate order:
1. `temp-bracing`
2. `bolting`
3. `qa-inspector`
4. `safety-failsafe`

Parent assembles Decision from gates. SafetyFailsafe FAIL => ABORT.
