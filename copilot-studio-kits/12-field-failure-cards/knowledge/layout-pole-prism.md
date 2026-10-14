# Common Layout Pole, 360 Prism, and Pole-Mounted Prism Failures

Source file: `layout_pole_prism_failures_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** Retrieval dataset for field AI agents diagnosing failures local to the moving total-station layout pole and its mounted target.

**Authority:** Project specifications, the licensed surveyor or survey lead, equipment manuals, calibration status, and site control authority govern. Agents must diagnose and contain; they must not silently alter control, calibration, or design data.

Record count in the source file: 64. Do not quote those records as this job.

## Out of this card

- Dedicated backsight prism, target, carrier, tribrach, and backsight tripod failures
- Instrument tripod, instrument tribrach, station centering, and instrument-settlement failures
- Control-network and resection geometry except as an independent known-point check
- GNSS rover-pole-only failures unless the same physical mechanism applies to a total-station target pole

## When this shows up

- **Nearly constant Z bias; XY is reasonable**
  Check first: physical point-to-optical-center height; active height record and measured-to method; tip and adapter height; 360 face-dependent elevation.
- **Error changes when pole or prism rotates**
  Check first: bubble adjustment; pole runout or bend; loose tip or adapter; 360 sector center; nonnodal prism orientation.
- **Scatter grows with pole height**
  Check first: pole lean; bubble sensitivity; bipod stability; wind and operator handling.
- **Error changes when reflector type changes**
  Check first: exact target model; prism constant and sign; correction authority; optical-center height; holder and adapter geometry.
- **Discrete jump after pole turns or line-of-sight loss**
  Check first: different 360 sector; wrong target reacquisition; reflective clutter; Target ID and tracking mode.
- **Short-range robotic instability**
  Check first: 360 sector ambiguity; target mode; fine versus rapid aim; partial obstruction.
- **Lateral miss grows with distance**
  Check first: robotic fine-aim or collimation; target centering; prism orientation; production-range known-point check.
- **One mark only is inconsistent**
  Check first: tip in drill hole or recess; debris or soft contact; point-center definition.
- **Gradual Z drift through the shift**
  Check first: friction-clamp creep; bipod settlement; pole section mark; temperature or handling event.
- **Fault follows one crew, pole, or kit**
  Check first: assembly identity; template version; measured assembly height; rotation test; target record.

## Do this

- Confirm the requested issue is local to the moving layout target and not a backsight or instrument-tripod problem.
- Classify the error signature: constant, rotational, height-dependent, range-dependent, target-dependent, point-specific, drifting, or lock-identity related.
- Isolate one measurement-chain layer at a time on a fixed known point.
- Preserve raw observations and configuration history before correction.
- Contain and bound affected work, correct the proven cause, and require independent release evidence.

## Never do

- Silently changing control coordinates, station setup, localization, site calibration, or design geometry to absorb a pole-target error
- Assuming a 360, flat, mini, circular, active, and passive reflector are interchangeable
- Applying an undocumented numerical correction to future stakes instead of repairing and verifying the assembly
- Resuming layout because one self-confirming point fits after an adjustment

## Handoff

Escalate to the survey lead when target identity, constant, measured-to reference, assembly geometry, instrument correction authority, or affected installed-work interval cannot be proven.


This card does not release the work.
