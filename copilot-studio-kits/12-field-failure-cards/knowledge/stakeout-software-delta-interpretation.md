# Common Stakeout Software Delta, Direction, Snap, Selection, and Storage Interpretation Failures

Source file: `stakeout_software_delta_interpretation_failures_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** Retrieval dataset for field AI agents diagnosing construction-layout failures caused by stakeout-software interpretation and state rather than measurement hardware.

**Authority:** Project specifications, approved design documents, current software manuals, the survey lead, and design/VDC authority govern. Agents diagnose and contain; they do not redefine design intent or control.

Record count in the source file: 64. Do not quote those records as this job.

## Out of this card

- Physical layout pole, backsight assembly, occupied station, and target-lock hardware failures
- Control-network and resection geometry except as external verification or prohibited masking actions
- CAD/BIM export and coordinate-transformation generation failures that exist before the file reaches stakeout software; those belong in the next data-import module
- Authorized design revisions and project-control decisions reserved to design, VDC, or survey leadership

## When this shows up

- **Moving as instructed increases the delta**
  Check first: sign convention; subtraction order; target/instrument perspective; line direction.
- **Correct magnitude on wrong side**
  Check first: line or arc direction; left/right convention; offset sign; perspective.
- **Z jumps by slab or object thickness**
  Check first: whole-object surface selection; top versus bottom face; multiple selected surfaces.
- **Grade changes while approaching station**
  Check first: surface at current position versus selected station; vertical versus perpendicular delta; wrong chainage.
- **Precise point conflicts with plans**
  Check first: design object identity; revision; direct linework provenance; snap mode; offset duplication.
- **Series is one interval ahead or behind**
  Check first: point increment; station interval; relative versus zero-based stationing; line direction.
- **Screen shows pass but raw check fails**
  Check first: display rounding; horizontal/vertical tolerance; default symbol color; fast versus precision mode.
- **New file is shifted dramatically**
  Check first: units; coordinate frame; coordinate order; grid/ground; calibration; revision.
- **Point number advances but export is missing observations**
  Check first: native job record; storage event; job integrity; connection/write failure.
- **Correct coordinate but wrong stake note**
  Check first: point identity; auto increment; attributes; as-staked/design relationship; report stylesheet.

## Do this

- Confirm measurement hardware and control have been routed to their own modules before changing stakeout software state.
- Classify the signature as delta/reference, direction/perspective, snap/selection, station/offset, unit/tolerance, file/version, storage/report, or recovery failure.
- Preserve source design and native job state and isolate one interpretation layer at a time.
- Stop and bound work whenever design identity or delta meaning is uncertain.
- Require known geometric examples plus final native storage evidence before release.

## Never do

- Changing control, station, localization, calibration, or design geometry to make a misinterpreted stakeout target fit
- Assuming zero deltas prove approved design identity
- Relying on color, auto increment, or a formatted report without reviewing numeric and native records
- Continuing a series after a revision, direction, offset, surface, unit, or tolerance change without a regression check

## Handoff

Escalate to survey, VDC, or design authority when source revision, coordinate frame, design object, derived snap/constraint, offset intent, or installed-work exposure cannot be proven.


Release rule: Resume only when source identity, software interpretation, known examples, final remeasurement, native storage, report output, and affected-work boundary all pass.

This card does not release the work.
