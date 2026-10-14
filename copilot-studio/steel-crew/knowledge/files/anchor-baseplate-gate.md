# Workflow: `anchor-baseplate-gate`

Gate order:
1. `survey-anchors`
2. `grout-baseplate`
3. `qa-inspector`
4. `safety-failsafe`

Parent assembles Decision from gates. SafetyFailsafe FAIL => ABORT.
