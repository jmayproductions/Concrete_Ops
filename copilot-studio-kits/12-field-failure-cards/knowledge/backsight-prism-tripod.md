# Common Backsight Prism, Tribrach, Carrier, and Target-Tripod Failures

Source file: `backsight_prism_tripod_failures_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** Retrieval dataset for field AI agents diagnosing failures in a dedicated total-station backsight target and the tripod supporting it.

**Authority:** Project specifications, the licensed surveyor or survey lead, current equipment manuals, calibration status, and site-control authority govern. An AI agent may diagnose and contain but must not silently alter control or orientation.

Record count in the source file: 64. Do not quote those records as this job.

## Out of this card

- The tripod, tribrach, centering, leveling, and settlement of the occupied total station itself
- Moving layout pole, bipod, pole tip, pole bubble, and pole-mounted layout target failures
- Resection and control-network geometry except where an independent reference is needed to test the backsight
- Control-authority decisions to create, adjust, replace, or publish project control

## When this shows up

- **Constant angular rotation of all layout**
  Check first: backsight point identity; target centering; short backsight; wrong reflector lock; stored orientation observation.
- **Backsight direction drifts over time**
  Check first: tripod feet and clamps; head screw; tribrach hysteresis; solar heating; vibration or contact.
- **Direction changes when carrier or prism rotates**
  Check first: plummet adjustment; carrier reseat repeatability; holder eccentricity; nonnodal prism aim; 360 face behavior.
- **Correct direction but wrong backsight distance**
  Check first: wrong point; prism constant and sign; double correction; prism orientation; expected inverse distance.
- **Correct horizontal orientation but wrong elevation**
  Check first: target height; measured-to method; carrier or adapter height; tilted or wrong prism; tripod settlement.
- **Manual aim and robotic aim disagree**
  Check first: ATR/Autolock calibration; visual versus optical center; nearby reflector; prism aim and target model.
- **Setup changes after component swap**
  Check first: matched kit identity; forced-centering axes; carrier height; target preset; prism constant.
- **Only distant layout fails**
  Check first: backsight line length; centering error; single-face pointing; independent long-range check.
- **Good initial setup, bad check after disturbance**
  Check first: contact event; foot or clamp marks; plummet and level; full reorientation; affected interval.
- **Setup fits one backsight but not other control**
  Check first: single-reference redundancy; moved control; wrong coordinates; centering; multiple-backsight or unused-point check.

## Do this

- Confirm the problem belongs to the dedicated backsight target and supporting tripod, not the occupied instrument tripod or moving layout pole.
- Classify the signature as identity, centering, time drift, rotation, height, distance, target-lock, geometry, or recovery failure.
- Preserve raw data and isolate one backsight-chain layer at a time.
- Contain and bound affected layout before recommending correction.
- Require independent release evidence rather than a single re-zeroed backsight.

## Never do

- Changing project control, site calibration, orientation, localization, or design coordinates merely to force one backsight to fit
- Accepting a centered bubble or a zero horizontal angle as proof of correct backsight setup
- Continuing after a backsight is bumped, moved, or reacquired without a full measured and independent check
- Assuming tribrachs, carriers, adapters, prism holders, target heights, and constants are interchangeable

## Handoff

Escalate to the survey lead whenever point identity, control integrity, optical or forced-centering axes, reflector constant, correction authority, or the installed-work exposure cannot be proven.


Release rule: Resume only when the repaired or rebuilt backsight passes complete physical, centering, metadata, measured-observation, and independent-control checks at representative geometry.

This card does not release the work.
