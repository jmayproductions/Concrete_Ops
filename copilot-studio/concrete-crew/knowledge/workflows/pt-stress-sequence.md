# Workflow: pt-stress-sequence

**Purpose:** Repeatable tendon stressing with elongation and cert discipline.

## Order
1. Confirm `pt-pre-stress-gate` was GO for this deck
2. `pt-stress` — execute/validate sequence; compare actual vs planned psi & elongation
3. `qc-inspector` — witness elongations / gauge readings
4. `crew-ops` — fatigue + radio discipline during jacking
5. `safety-failsafe` — strand/anchorage incidents force ABORT
6. `pt-stress` — inspection + certification status for stressed tendons

## Pass rule
Any elongation/psi outside tolerance → HOLD that tendon (do not bury it). Broken strand / anchorage failure → ABORT.
