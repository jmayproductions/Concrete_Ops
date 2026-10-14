# Elevation Delta Measurement Issues

Source file: `elevation_delta_measurement_issues_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** Retrieval-augmented field AI agents diagnosing elevation, delta-Z, benchmark, grade, vertical-control, total-station, and software discrepancies.

**Authority:** Any unexplained elevation delta affecting control or installed work requires containment and review under project procedures. This dataset does not authorize benchmark, datum, design, or installed-work changes.

Record count in the source file: 68. Do not quote those records as this job.

## When this shows up

- **All elevations high or low by nearly the same amount**
  Check first: Target height; instrument height; occupied elevation; benchmark value and datum; architectural-to-survey datum offset.
- **Delta grows with distance**
  Check first: Vertical index; refraction and curvature; long sight; atmospheric correction; reciprocal observation.
- **Delta grows with steepness or changes on upward versus downward sights**
  Check first: Vertical index; target angular range; prism constant and geometry; pole tilt; reflectorless incidence.
- **Face 1 and face 2 disagree**
  Check first: Vertical-index adjustment; collimation; compensator; crosshair aiming; reflectorless beam alignment.
- **Delta changes over minutes, hours, or construction events**
  Check first: Thermal acclimation; tripod settlement; benchmark movement; pole slip; near-ground refraction.
- **Delta tilts or changes across the site**
  Check first: Geoid; inclined-plane calibration; control distribution; extrapolation; surface/model revision.
- **Only one benchmark or point is wrong**
  Check first: Point identity; disturbance; rod contact; wrong HT on one observation; duplicate point record.
- **Repeated shots scatter without a stable direction**
  Check first: Pole plumb and bubble; tripod and level; target lock; weather and reflectorless return; instrument service condition.
- **Point below reads above, or offset goes the correct amount the wrong way**
  Check first: Zenith/elevation-angle convention; VD sign; inverted target height; vertical offset perspective; cut/fill convention.
- **Previously stored elevation changes after import, calibration, or edit**
  Check first: Height-record edit history; stored vector versus position; active calibration/geoid; duplicate import; model revision.

## Do this

- Treat any unexplained elevation delta as uncontained until the last passing independent vertical check and affected-work boundary are known.
- What is the canonical delta sign: observed minus expected, or the software's local cut/fill convention?
- Is the delta constant, distance-correlated, angle-correlated, face-dependent, time-dependent, location-dependent, one-point-only, random, or sign-reversed?
- What exact occupied elevation, HI, raw VA, slope distance, corrections, HT, target, benchmark, datum, geoid, calibration, and expected design elevation were active?
- What independent benchmark, second face, reciprocal observation, closed loop, or second instrument can discriminate the cause?
- What work occurred after the last passing independent vertical check?

## Never do

- Never add an unexplained Z offset merely to make a check pass.
- Never average a gross vertical outlier into control.
- Never treat a single benchmark, single face, single one-way sight, or internal setup residual as independent proof.
- Never change an approved benchmark, vertical datum, geoid, design grade, or installed-work disposition without the responsible authority.

## Handoff

Open a hold and route it to the person named in the project safety and quality plan. This card does not name that person and does not close the hold.

This card does not release the work.
