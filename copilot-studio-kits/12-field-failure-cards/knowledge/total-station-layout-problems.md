# Total Station Construction Layout Problems

Source file: `total_station_layout_problems_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** Retrieval-augmented field AI agents that diagnose construction-layout problems involving total stations, controllers, BIM/CAD data, and field software.

**Authority:** The dataset supports troubleshooting and QA/QC; it does not replace a licensed surveyor, project control authority, approved plans, manufacturer service, or project-specific tolerances.

Record count in the source file: 134. Do not quote those records as this job.

## When this shows up

- This module has no symptom router. Use the questions and stop rules below.

## Do this

- What instrument, controller, field software, and versions are in use?
- Is the error horizontal, vertical, distance-proportional, constant, or intermittent?
- What setup method, control points, target type, target height, and prism constant were used?
- What units, coordinate system, datum, scale factor, and design revision are active?

## Stop work when

- Independent check point fails project tolerance.
- Control identity, datum, units, scale, or current design revision cannot be proven.
- Instrument was bumped, moved, dropped, or is outside compensator/calibration range.
- Robot may be locked to the wrong target or reflector.
- Residuals are being hidden by loosening tolerances rather than explained.
- Layout conflicts with approved drawings or another trade's verified control.

## Handoff

Return ranked hypotheses and discriminating checks before recommending a fix. Never tell a field user to continue critical layout solely because a software residual is green.

This card does not release the work.
