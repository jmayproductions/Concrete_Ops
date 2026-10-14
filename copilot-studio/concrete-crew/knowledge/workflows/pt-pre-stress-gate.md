# Workflow: pt-pre-stress-gate

**Purpose:** Same GO/HOLD/ABORT before PT jacks roll every deck.

## Order (do not reorder)
1. `pt-stress` — strength ≥ min, tendon inventory, spacing, sequence published
2. `qc-inspector` — cylinder/maturity evidence supporting stress strength
3. `crew-ops` — PT crew roles + briefing (include exclusion zone)
4. `safety-failsafe` — barriers / stop-work clear
5. `pour-lead` — assemble stress-day plan and decision

## Pass rule
All PASS (ADVISORY ok). Missing strength or incomplete inventory → HOLD. Anchorage/safety FAIL → ABORT.
