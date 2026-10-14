# Total Station Calibration, Collimation, Compensator, EDM, Atmosphere, Tribrach, and Service Failures

Source file: `total_station_calibration_environment_failures_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** Retrieval dataset for field AI agents diagnosing optical, mechanical, electronic-distance, atmospheric, centering, environmental, adjustment, and service-state failures in construction total-station layout.

**Authority:** The instrument-specific manual, project tolerance, survey lead, authorized service provider, and current service/calibration evidence govern. Agents may diagnose and contain but must not invent calibration values or authorize mechanical repairs.

Record count in the source file: 64. Do not quote those records as this job.

## Out of this card

- Control-network design, site-control establishment, occupied-point selection, resection geometry, and coordinate-system transformation except as independent test references
- Pole bubbles, pole straightness, handheld 360/flat prism mounting, backsight tripod/prism setup, and target-lock search behavior except when isolating instrument calibration
- Stakeout delta/sign/display interpretation, point/file selection, storage, and CAD/BIM import transform failures
- Unauthorized mechanical disassembly, internal laser repair, sealed adjustment, or service operations reserved to qualified technicians

## When this shows up

- **Face 1 and Face 2 disagree laterally**
  Check first: horizontal collimation; balanced face set; manual versus Autolock; target stability.
- **One-face elevations are biased but two-face mean improves**
  Check first: vertical index; vertical collimation; standing-axis tilt; target/instrument height routed elsewhere.
- **Horizontal error grows on high or low targets**
  Check first: trunnion axis; standing axis; compensator index/state/range; steep-sight check.
- **Angle changes as telescope elevates along a plumb line**
  Check first: instrument level; compensator action; standing-axis error; plate/bubble adjustment.
- **Constant in/out distance error**
  Check first: physical prism; prism constant sign/profile; instrument/controller override; EDM additive constant; DR mode.
- **Distance error grows with range**
  Check first: temperature and pressure; PPM; EDM frequency/scale; sea-level/projection/station scale.
- **Vertical error grows with long low sight**
  Check first: heat shimmer/refraction; curvature/refraction correction; vertical index; two-face/reciprocal check.
- **Level or center moves after rotation/touch**
  Check first: tribrach clamp; footscrew backlash; plummet rotation; bubble rotation; tripod torsion.
- **Adjustment values jump after temperature/transport**
  Check first: acclimation; repeat observation; stable setup; impact/mechanical service threshold.
- **Manual aim and tracker aim disagree**
  Check first: optical collimation first; tracker/ATR collimation; target type; wrong adjustment sequence.
- **Reflectorless distance jumps at edges/glass/mesh**
  Check first: beam footprint; mixed surface return; incidence angle; DR distance window; cooperative target check.
- **Service certificate exists but field checks fail**
  Check first: instrument serial/certificate identity; tribrach and target system; controller profiles; atmosphere; post-service golden test.

## Do this

- Route design/control/setup/pole/backsight/tracking/display symptoms to their modules, but first identify whether the same fault follows this instrument across stable independent tests.
- Classify the signature as face/collimation, trunnion/index, compensator/level, EDM/constant, atmosphere/refraction, tribrach/plummet, thermal/mode, or service/recovery.
- Preserve raw observations and current corrections before any adjustment; isolate one layer at a time with a stable independent reference.
- Use face reversal, steep-sight dependence, rotation tests, fixed-versus-proportional distance residuals, mode swaps, and time/temperature trends to discriminate causes.
- Stop and escalate whenever values are extreme, unstable, repeatedly fail, or imply mechanical damage or untraceable installed-work exposure.

## Never do

- Adjusting project control, station coordinates, localization, design data, or target heights to absorb an instrument calibration error
- Entering arbitrary internal correction values or mechanically opening/sealed-adjusting the instrument without authorization
- Disabling compensators, forcing low-quality EDM acceptance, or relying on one face/one distance/one backsight to bypass failed checks
- Correcting reduced coordinates without preserving native raw observations, target identity, correction lineage, and affected-work interval
- Returning a repeatedly failing or mechanically unstable instrument to production because the software eventually displayed success

## Handoff

Escalate to the survey lead and authorized service provider when adjustment values exceed limits, fail to repeat, calibrations fail, EDM baseline residual remains, mechanical interfaces move, service lineage is missing, or critical installed work may be affected.


Release rule: Release only when the complete instrument-target-tribrach-controller system passes stable centering/level, balanced angular, steep-sight, tracker/manual, multi-distance, atmospheric, known-control, raw-record, and affected-work checks within project tolerance.

This card does not release the work.
