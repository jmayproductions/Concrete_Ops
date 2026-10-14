# Workflow: pour-day-runbook

**Purpose:** Execute placement with the same station discipline every pour.

## Order
1. Confirm `pre-pour-gate` already GO for this pour ID
2. `crew-ops` — final headcount and radio check
3. `pour-lead` — start pour, zone sequence, pump path
4. `qc-inspector` — first-truck slump + temp
5. `weather-gate` — watch window during placement
6. `safety-failsafe` — continuous threshold watch
7. `pour-lead` — end pour with yards, times, exceptions

## Pass rule
Pour may continue only while QC criticals and fail-safe remain clear. First FAIL from safety → ABORT placement.
