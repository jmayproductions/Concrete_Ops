# Common Resection Geometry Issues

Source file: `resection_geometry_issues_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** Retrieval-augmented field AI agents diagnosing total-station resection/free-station geometry, control distribution, redundancy, residuals, work-area validity, and acceptance failures.

**Authority:** A computed station or small residual does not authorize production layout. Project tolerances, control authority, independent checks, and affected-work procedures govern acceptance.

Record count in the source file: 64. Do not quote those records as this job.

## When this shows up

- **Solution computes from two points but there is no unused check**
  Check first: Add or reserve a third point; Check horizontal and vertical redundancy; Do not release production.
- **All controls appear through one narrow opening**
  Check first: Calculate bearing span; Move station or add an off-sector point; Check orientation uncertainty.
- **Controls are almost in one straight line through the station**
  Check first: Add off-line control; Test cross-track sensitivity; Reject critical two-point geometry.
- **Many points exist but all are on one side**
  Check first: Map quadrants and hull; Add opposite-side control; Restrict work area.
- **Near checks pass but far layout fails**
  Check first: Compare control distance with work radius; Use a longer baseline; Check remotely.
- **Work is beyond or outside every resection point**
  Check first: Stop extrapolated layout; Extend control; Check at the work boundary.
- **Horizontal is good but elevation is unstable**
  Check first: Inspect 1D contributors and redundancy; Verify HT and benchmarks; Transfer elevation independently.
- **Station moves when one control point is removed**
  Check first: Run all leave-one-out solutions; Verify the dominant point; Review weights and control provenance.
- **One observation or round does not repeat**
  Check first: Verify target, HT, prism, pole, face, and setup stability; Repeat raw observations; Invalidate mixed-state data.
- **Residuals are small but an unused point fails**
  Check first: Trust the external failure; Audit control and coordinate state; Do not force the fit.
- **Setup changes after calibration or coordinate-system revision**
  Check first: Freeze both states; Recompute cleanly; Repeat resection under approved final state.

## Do this

- If resection geometry or validation is uncertain, stop control-dependent layout, preserve the complete setup, and test an unused point before changing observations or control.
- How many independent points and which observation components contribute to horizontal and vertical solutions?
- What are the azimuth span, quadrant distribution, station position relative to the control hull, control distance range, and furthest work radius?
- What are the individual residuals, E/N/Z and orientation standard errors, redundancies, and leave-one-out station shifts?
- Which point was not used in the solution and what was its check error at representative work geometry?
- What control revision, coordinate system, calibration, target, HT, prism, faces, and setup state were active?

## Never do

- Never accept a resection because it merely computed.
- Never equate small internal residuals with correct project coordinates.
- Never delete or down-weight a control point solely to obtain a passing result.
- Never extrapolate setup statistics outside the control envelope without boundary checks.
- Never change the coordinate system, calibration, or authoritative control after resection without recomputing and revalidating the station.

## Handoff

Open a hold and route it to the person named in the project safety and quality plan. This card does not name that person and does not close the hold.

This card does not release the work.
