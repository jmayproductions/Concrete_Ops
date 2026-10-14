# Workflow: tilt-up-lift-day

**Purpose:** Erect-day runbook — pick, brace, release — identical every panel.

## Order
1. `tilt-up` — strength-for-lift, lift order, crane chart, pick points, braces staged
2. `weather-gate` — wind first; HOLD if over tilt wind limit
3. `crew-ops` — tilt roles present (tilt_lead, crane_operator, rigger, brace_crew, qc_tech, safety_watch)
4. `qc-inspector` — panel marks + brace hardware verified
5. `safety-failsafe` — exclusion zone / stop-work
6. `tilt-up` — brace secured before crane release
7. `pour-lead` — continue / hold next panel decision

## Pass rule
Wind HOLD or incomplete braces → do not pick / do not release. Safety FAIL → ABORT lift.
