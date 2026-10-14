# Workflow: tilt-up-brace-release

**Purpose:** Close temporary bracing only when structure/engineer criteria are met.

## Order
1. `tilt-up` — permanent connections complete per sequence
2. `qc-inspector` — weld/bolt inspection accepted
3. `crew-ops` — brace-removal crew + fall protection plan
4. `safety-failsafe` — no residual instability flags
5. `tilt-up` — release braces panel-by-panel per engineer order

## Pass rule
Incomplete permanent connections → HOLD. Any instability → ABORT and re-brace.
