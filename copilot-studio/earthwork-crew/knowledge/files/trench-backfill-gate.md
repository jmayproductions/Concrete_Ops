# Workflow: `trench-backfill-gate`

Gate order:
1. `utilities-locate`
2. `trench-backfill`
3. `compaction`
4. `safety-failsafe`
5. `qa-inspector`

SafetyFailsafe FAIL => ABORT.
