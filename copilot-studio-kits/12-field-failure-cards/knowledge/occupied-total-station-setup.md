# Common Occupied Total-Station Setup, Tripod, Tribrach, Height, and Calibration Failures

Source file: `occupied_total_station_setup_failures_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** Retrieval dataset for field AI agents diagnosing failures local to the occupied total station and its physical, calibration, and computation state.

**Authority:** Project specifications, current manufacturer manuals, the licensed surveyor or survey lead, calibration authority, and control governance supersede this dataset. Agents diagnose, contain, and require evidence; they do not silently recalibrate or alter control.

Record count in the source file: 64. Do not quote those records as this job.

## Out of this card

- Dedicated backsight prism, carrier, tribrach, target tripod, and backsight point-contact failures
- Moving layout pole, pole tip, pole bubble, bipod, and pole-mounted target failures
- Resection geometry and control-network design except as an independent check or prohibited masking action
- Project-control adjustment or publication decisions reserved to the licensed surveyor or authorized control lead

## When this shows up

- **All layout translated or rotated consistently**
  Check first: occupied point identity; station centering; backsight orientation; independent control.
- **Backsight zero drifts over minutes**
  Check first: tripod feet and clamps; head and fixing screw; tribrach hysteresis; warm-up; sun and vibration.
- **Center changes when instrument rotates**
  Check first: laser or optical plummet; tribrach axis; head torsion; instrument seating.
- **Correct horizontal layout but constant Z error**
  Check first: instrument height; HI method and reference; HI edit interval; target height.
- **F1 and F2 disagree**
  Check first: HA/VA collimation; vertical index; trunnion axis; unstable setup; compensator.
- **Manual and robotic aim disagree**
  Check first: ATR or Autolock collimation; target center; instrument stability; calibration order.
- **Distance error grows with range**
  Check first: PPM and atmosphere; scale factor; EDM constant; prism correction.
- **Vertical error grows on long or steep sights**
  Check first: vertical index; trunnion axis; curvature/refraction; compensator; HI.
- **First checks fail, later checks stabilize**
  Check first: tripod stress relaxation; thermal equilibration; instrument warm-up; ground settlement.
- **Error follows one job or controller template**
  Check first: instrument profile; measurement mode; correction state; scale and atmosphere; HI method.

## Do this

- Confirm the fault is local to the occupied station rather than the dedicated backsight or moving layout target.
- Classify the signature: identity, centering, time drift, height, level, face, aim, distance scale, correction state, or recovery failure.
- Preserve raw data and isolate one station-chain layer at a time.
- Contain and conservatively bound affected layout before correction.
- Require measured backsight plus unused-control evidence before release.

## Never do

- Altering control, orientation, localization, calibration, resection coordinates, or design data merely to make one setup fit
- Assuming the compensator corrects station translation, torsion, settlement, or wrong point occupation
- Repeating calibration until values appear acceptable without correct setup geometry and independent verification
- Releasing layout after a bump, drift, failed face check, or uncertain correction state without bounding affected work

## Handoff

Escalate to the survey lead or qualified service provider when control identity, instrument axes, compensator, plummet, calibration authority, computation state, or affected installed-work interval cannot be proven.


Release rule: Resume only after physical stability, centering, level, HI, calibration, correction state, measured backsight, and an unused control check all pass and the affected interval is bounded.

This card does not release the work.
