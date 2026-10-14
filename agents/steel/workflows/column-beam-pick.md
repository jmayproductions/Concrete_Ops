# Workflow: `column-beam-pick`

Gate order:
1. `crane-logistics`
2. `temp-bracing`
3. `bolting`
4. `plumb-alignment`
5. `safety-failsafe`

Parent assembles Decision from gates. SafetyFailsafe FAIL => ABORT.
