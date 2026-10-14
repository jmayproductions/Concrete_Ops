# Drone/UAS Construction Mapping, Progress, RTK/PPK, and Flight-Safety Failures

Source file: `drone_uas_construction_mapping_progress_failures_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** RAG dataset for field/VDC AI agents preventing illegal or unsafe construction UAS flights and preventing inaccurate imagery, surfaces, quantities, progress comparisons, or exports from driving field decisions.

**Authority:** The remote pilot in command has final operational authority and responsibility for safe flight. Current FAA rules/authorizations/waivers, state/local/tribal requirements, owner/site rules, privacy obligations, project specifications, qualified survey/design professionals, and contract authority govern. This dataset is diagnostic support, not legal advice or flight authorization.

**Beside the other kits:** This card does not authorize a flight or the use of a map as as-built.

Record count in the source file: 64. Do not quote those records as this job.

## When this shows up

- **Map is globally shifted**
  Check first: base coordinates; RTK fix per image; GCP/checkpoint roles; CRS/units/site calibration; independent checkpoint vectors.
- **XY fits but Z is wrong**
  Check first: ellipsoid versus geoid; vertical CRS; antenna height; base elevation; double transform.
- **Corridor bends or strips step**
  Check first: single-line geometry; sidelap/cross-lines; boresight/lever arm; trajectory timing; two-sided checkpoints.
- **Ortho has seams or doubled equipment**
  Check first: mixed time states; moving objects; DSM; exposure/shadows; source image/seam.
- **RTK dropped mid-flight**
  Check first: per-image status; raw observations; RINEX coverage; PPK recovery; checkpoint pattern.
- **No ground under vegetation/water/snow**
  Check first: direct visibility; tie-point support; classification; artifact mask; alternative survey/LiDAR.
- **Stockpile or cut/fill changes unexpectedly**
  Check first: base surface/boundary; common datum/control; coverage; processing equivalence; material density/swell.
- **Saved flight is suddenly unsafe**
  Check first: current cranes/obstacles; people/traffic; airspace/TFR; weather/wind; RTH/failsafe.

## Do this

- Separate legal/safety fitness from mapping fitness.
- Preserve raw state and trace the full pilot-to-export lineage.
- Use per-image telemetry, independent checkpoints, spatial residuals, and one-variable reprocessing to discriminate faults.
- Hold flights and downstream decisions until qualified authorities sign the relevant gates.

## Never do

- Flying because an app appears green when authority or site safety is not proven
- Changing control/datum/processing to force agreement
- Calling RTK/GCP output survey-grade without independent evidence and authority
- Measuring invented/hidden surfaces or comparing uncontrolled epochs
- Releasing quantities/progress from unverified exports or unreproducible projects

## Handoff

Escalate to the remote PIC for every operational decision and to qualified survey/VDC/QC/design/owner authority whenever accuracy, datum, control, processing, quantity, progress, layout, professional-scope, or contractual use is uncertain.


Release rule: Flight and data release require independent legal/airspace, jobsite safety, capture completeness, GNSS/control, processing, checkpoint, comparison, export, archive, and authority gates; passing one gate never substitutes for another.

This card does not release the work.
