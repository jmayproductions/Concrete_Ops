# Workflow: mid-pour-monitor

**Purpose:** Fast health check while concrete is flowing.

## Order
1. `qc-inspector` — latest slump/temp/cylinder status
2. `weather-gate` — current conditions vs thresholds
3. `safety-failsafe` — telemetry vs rules
4. `crew-ops` — fatigue / incident flags
5. `pour-lead` — continue / slow / stop recommendation

## Cadence
Run at first truck, every 50 CY, weather change, or any crew-raised concern.
