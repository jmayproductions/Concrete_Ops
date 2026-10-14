# Workflow: pre-pour-gate

**Purpose:** One repeatable GO/HOLD/ABORT decision before trucks roll.

## Order (do not reorder)
1. `materials-mix` — accept mix ticket / design envelope
2. `weather-gate` — CLEAR or HOLD with protocol
3. `qc-inspector` — pre-pour checklist
4. `crew-ops` — required roles + fatigue clear + briefing complete
5. `safety-failsafe` — no critical violations
6. `pour-lead` — assemble final placement plan and decision

## Pass rule
All gates PASS (weather may be ADVISORY). Any FAIL from safety → ABORT. Any other FAIL/incomplete → HOLD.
