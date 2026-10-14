# Construction Site Control Setup Failures

Source file: `site_control_setup_failures_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** Retrieval-augmented field AI agents diagnosing establishment, transfer, setup, preservation, verification, and recovery failures in construction site control.

**Authority:** Control acceptance, datum changes, monument replacement, and disposition of installed work must follow the project documents and responsible licensed or design authority. The dataset supports diagnosis and QA/QC; it does not authorize field changes.

Record count in the source file: 87. Do not quote those records as this job.

## When this shows up

- **Nearly the same horizontal delta at every known point**
  Check first: Occupied point identity; local versus project coordinates; datum realization; active shared-coordinate site; control revision.
- **Transverse error grows with distance from the setup**
  Check first: Backsight identity; typed azimuth; short orientation baseline; project north versus grid north; resection angular spread.
- **Error grows in proportion to distance**
  Check first: Grid versus ground; US survey foot versus international foot; combined scale factor; units parser; prism constant for additive distance bias.
- **Horizontal agrees but every elevation is high or low**
  Check first: Instrument height; target height; benchmark datum; ellipsoid versus orthometric height; active geoid.
- **Residual magnitude or direction changes across the site**
  Check first: Calibration geometry; extrapolation outside control; double transform; one-sided network; bad control included in fit.
- **Checks change by date, temperature, loading, or construction event**
  Check first: Monument settlement; tripod or mount stability; thermal acclimation; structure movement; disturbance history.
- **One control fails while the rest agree**
  Check first: Physical mark identity; disturbance; wrong target lock; duplicate point ID; benchmark movement.
- **Repeated observations scatter without a stable pattern**
  Check first: Tripod and tribrach; rod bubble and target; wrong lock; weather and vibration; instrument calibration.
- **Different crews or software show different values under the same IDs**
  Check first: Revision and checksum; duplicate IDs; active transform and calibration; field edits; sync status.
- **Setup computed but there is no unused check point**
  Check first: Add independent control; redesign setup geometry; retrieve authoritative control; do not release production.

## Do this

- If a control discrepancy is unexplained, stop control-dependent layout, preserve evidence, identify the last passing independent check, and bound affected work before proposing a correction.
- What was the last independent check that passed, and when?
- Is the error a constant shift, rotation growing with distance, proportional scale, vertical-only bias, spatial warp, time drift, one-point outlier, or random scatter?
- Which exact control revision, datum, units, grid/ground policy, transform, geoid, occupied point, backsight/resection points, HI, HT, and target were active?
- What layout or installed work occurred after the last passing check?

## Never do

- Never average, translate, rotate, scale, calibrate, or delete an observation solely to make residuals pass.
- Never treat low internal residuals as proof that the datum, scale, control coordinates, or design file are correct.
- Never resume critical layout from a repaired setup without an independent check not consumed by the solution.
- Never change authoritative control coordinates, datum, benchmark elevation, or installed-work disposition without the required project authority.

## Handoff

Open a hold and route it to the person named in the project safety and quality plan. This card does not name that person and does not close the hold.

This card does not release the work.
