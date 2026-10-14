# Workflow: `plumb-alignment-check`

Gate order:
1. `plumb-alignment`
2. `survey-anchors`
3. `qa-inspector`

Parent assembles Decision from gates. SafetyFailsafe FAIL => ABORT.
