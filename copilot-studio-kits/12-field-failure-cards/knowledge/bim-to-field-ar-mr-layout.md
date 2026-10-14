# BIM-to-Field Augmented and Mixed Reality Layout, Registration, and QA Failures

Source file: `bim_to_field_ar_mr_layout_failures_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** RAG dataset for field/VDC AI agents diagnosing BIM-to-field AR/MR failures and preventing attractive but unverified overlays from driving layout, installation, QA acceptance, or safety-critical decisions.

**Authority:** AR/MR is not a substitute for approved survey/layout methods, current design documents, competent-person safety controls, or qualified professional judgment. Project requirements and responsible authorities control.

Record count in the source file: 64. Do not quote those records as this job.

## When this shows up

- **constant whole-model translation/rotation/scale**
  Check: coordinate transform; datum/units; marker pose; site calibration.
- **error grows with distance or walking**
  Check: SLAM drift; anchor lever arm; short registration baseline; scale/grid-ground.
- **sudden jump or post-restart offset**
  Check: loop closure; tracking loss/relocalization; wrong marker; persistent-anchor mismatch.
- **only one discipline/export is wrong**
  Check: federation/link transform; origin/pivot conversion; view/phase/filter; unsupported geometry.
- **view-angle, surface, or lighting dependent**
  Check: parallax; depth/occlusion; poor features; reflective/transparent surfaces; device fit/calibration.
- **different users/devices disagree**
  Check: cross-device anchors; device/software matrix; fit/eye calibration; stale model/cache.

## Do this

- Classify the intended field decision and tolerance.
- Separate source-model/coordinate errors from registration/tracking and perception errors.
- Preserve evidence and find the fastest independent control test.
- Contain all outputs since the last passing check.
- Escalate to the authority responsible for survey, VDC/model, design, QA, or safety.

## Never do

- Nudging an overlay to force visual agreement
- Using consumer AR/GPS/depth as survey control without demonstrated approval
- Continuing layout through drift/tracking loss
- Treating screenshots as measurement evidence
- Hiding conflicting model disciplines or stale revisions

## Handoff

Escalate survey/control/datum/tolerance questions to qualified survey or layout authority; model/revision/export questions to BIM/VDC and design authority; jobsite visibility/PPE/work-zone questions to the competent safety authority.


Release rule: A clean overlay, successful marker scan, green tracking state, RTK fix, or low fit residual is never sufficient alone. Release requires current design, proven coordinate/anchor integrity, independent checks, bounded drift, safe operation, and authorized signoff.

This card does not release the work.
