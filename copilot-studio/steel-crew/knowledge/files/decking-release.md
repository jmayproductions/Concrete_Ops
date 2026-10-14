# Workflow: `decking-release`

Gate order:
1. `decking`
2. `plumb-alignment`
3. `bolting`
4. `temp-bracing`
5. `safety-failsafe`

Parent assembles Decision from gates. SafetyFailsafe FAIL => ABORT.
