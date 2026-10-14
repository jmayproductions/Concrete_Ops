# Workflow: hold-abort

**Purpose:** Standard language and escalation when a gate fails.

## HOLD
- State the blocking gate and missing/failed item
- Name the owner who can clear it
- Re-run only the failed gate + `safety-failsafe` before release

## ABORT
- Triggered by `safety-failsafe` FAIL or structural unreadiness
- Stop placement, secure the deck, notify pour lead + superintendent
- Preserve evidence (tickets, readings, photos, timestamps)
- Require explicit re-entry through `pre-pour-gate`
