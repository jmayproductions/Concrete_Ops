# Reality Capture, Point-Cloud, Scan-to-BIM, Registration, and Inspection Failures

Source file: `reality_capture_pointcloud_scantobim_failures_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** RAG dataset for field AI agents diagnosing and containing construction reality-capture failures before point clouds, scan-derived models, inspections, or exports drive layout, fabrication, acceptance, or record decisions.

**Authority:** The executed contract, current issued model/drawings, licensed survey/design authority, project accuracy plan, equipment specifications at actual conditions, approved software versions, owner requirements, and jurisdiction govern. A vendor metric or forum solution is diagnostic evidence, not automatic acceptance authority.

Record count in the source file: 64. Do not quote those records as this job.

## Out of this card

- Drone aviation regulation, airspace authorization, flight safety, remote-pilot compliance, and site-specific safety planning except as capture-quality context
- Primary survey network design or adjustment, contractual tolerance selection, engineering acceptance, destructive repair design, or professional liability determinations by an unauthorized agent

## When this shows up

- **Double wall or local seam**
  Check first: isolate source scans; pairwise overlap and correspondence; moving scene; bad link; filter/mesh artifact.
- **Long corridor curves or thickens**
  Check first: trajectory or station order; loop closure; repetitive geometry; level/inclinometer mismatch; distributed checkpoints.
- **Bundle is tight but CAD/control misses**
  Check first: relative versus absolute accuracy; units/axis/scale; target-center constants; import mode; held-out control.
- **Far surface is sparse**
  Check first: point spacing at range; incidence angle; return intensity; occlusion; filter/decimation.
- **Floating points near glass or metal**
  Check first: raw setup rays; reflection/transmission; incidence; photos; independent measurement.
- **Photogrammetry splits into components**
  Check first: image overlap graph; blur/exposure/focal changes; weak texture; camera priors; bridging imagery/control.
- **Green heatmap conflicts with survey checks**
  Check first: reference revision; shared transform; distance definition; tolerance palette; coverage/exclusions.
- **Export opens at origin or shifted**
  Check first: source and target CRS; local origin; units/scale/offset; import/export mode; three-point round trip.
- **Small features disappear downstream**
  Check first: raw versus derivative density; decimation; filter/classification; mesh smoothing; downstream clipping.
- **Project crashes or becomes unusably slow**
  Check first: immutable backup; software/version/dependency; region/scan count; hardware/index/cache; validated tiled derivative.

## Do this

- Identify the exact downstream decision, feature/surface, work state, tolerance, required measurement direction, accuracy budget, and authoritative reference revision/frame.
- Preserve raw/native state and trace the suspect result backward through export, inspection, model/mesh, filters, registration/trajectory, control/targets, and capture geometry.
- Use isolated raw evidence, one-variable tests, link/trajectory network review, visual slices, density/intensity/coverage maps, and held-out distributed checkpoints to discriminate causes.
- Hold affected decisions and work until recapture/correction, independent verification, derivative revalidation, exposure review, and signed release are complete.

## Never do

- Aligning a failed cloud to design or deleting contrary evidence to make a report pass
- Calling holes empty space, mesh-filled areas measured surfaces, or idealized BIM objects exact as-builts without direct point support
- Using control residuals, overlap percentage, average bundle error, point density, or color-map appearance as a standalone accuracy statement
- Exporting only visible/clean data without an approved coverage and exclusion manifest
- Allowing scan-derived layout or acceptance to resume before held-out checks and a clean-environment data round trip pass

## Handoff

Escalate to the qualified survey/reality-capture lead and designated designer/QC/owner authority whenever tolerance or method capability is unclear, control/checkpoints fail, registration is weak or deformed, capture is incomplete, critical geometry is inferred, materials corrupt returns, processing is destructive, reference/metric is ambiguous, or released coordinates/content cannot be reproduced.


Release rule: Release only when capture fitness/completeness, immutable raw provenance, independent control/checkpoints, registration or trajectory redundancy, artifact/inference disclosure, authorized inspection logic, coordinate-safe derivatives, and clean-environment archive/readback all pass for the intended decision.

This card does not release the work.
