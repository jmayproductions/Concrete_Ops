# CAD/BIM Import, Coordinate Transformation, Scale, Rotation, Datum, and Federation Failures

Source file: `cad_bim_coordinate_transform_failures_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** Retrieval dataset for field AI agents diagnosing design-data and coordinate-transform failures before or during total-station construction layout.

**Authority:** The approved survey basis, current contract documents, current manufacturer documentation, and project survey/VDC/design authority govern. Agents diagnose, preserve evidence, and contain risk; they do not invent coordinate transformations or redefine design intent.

Record count in the source file: 64. Do not quote those records as this job.

## Out of this card

- Physical pole, prism, backsight, tripod, occupied station, resection geometry, tracking, search, and lock failures
- Stakeout display direction, cut/fill sign, snap, tolerance, and storage interpretation once a verified design package is already loaded
- Survey-control establishment or datum decisions reserved to a qualified project survey authority
- Design changes or acceptance of out-of-tolerance installed work reserved to design and project leadership

## When this shows up

- **Everything is uniformly 3.28084, 12, 1000, or reciprocal**
  Check first: native versus host units; file unit metadata; insertion scale; duplicate export scale.
- **Local dimensions work but state-plane coordinates shift feet**
  Check first: international versus U.S. survey foot; large coordinate magnitude; export unit metadata.
- **One point matches and error grows with distance**
  Check first: rotation; scale; one-point georeference; grid/ground; wrong scale origin.
- **All points have nearly the same XY shift**
  Check first: origin choice; wrong named site; datum realization; missing world file; manual link move.
- **Dimensions agree but left/right is mirrored**
  Check first: negative scale; reflection; axis swap; handedness; collinear control ambiguity.
- **Model lies on side or elevation appears in a horizontal axis**
  Check first: Y-up versus Z-up; axis order; export coordinate mapping.
- **XY fits but every Z is wrong by a constant**
  Check first: project zero; vertical datum; ellipsoid versus orthometric; vertical translation option; Z units.
- **Z residual changes across project**
  Check first: wrong geoid; tilted 3D alignment; surface warp; vertical datum realization.
- **Only some IFC objects are shifted**
  Check first: nested local placements; map conversion; linked/nested model transform; exported representation.
- **Source is correct but derivative is wrong**
  Check first: export unit metadata; coordinate base option; view/layer inclusion; curve tolerance; cache.
- **One discipline or building is rotated**
  Check first: shared versus internal aggregation; named site; instance transform; duplicate model; true north.
- **Field package differs across controllers**
  Check first: world sidecar; file hash; cache; resolved dependency path; job coordinate system.

## Do this

- Confirm the symptom belongs to design-data transformation rather than measurement hardware, control occupation, resection, target tracking, or stakeout-display interpretation.
- Classify the signature as units/scale, origin/georeference, rotation/axis, CRS/grid-ground, vertical datum, export semantics, file identity, or QA/recovery.
- Preserve pristine sources and build the full transform chain before changing any parameter.
- Use ratio, vector, signed-angle, determinant, plane-residual, hash, and independent-control tests to discriminate causes.
- Stop layout and bound affected work whenever design identity or any transform component is unproven.

## Never do

- Eyeballing, nudging, or scaling authoritative geometry until it appears to overlay
- Changing survey control, localization, station coordinates, or calibration to compensate for a bad design transform
- Accepting one matching point, a familiar-looking model, or zero stakeout deltas as proof of coordinate correctness
- Flattening datum, epoch, geoid, shared-site, or unit ambiguity into an undocumented local offset
- Overwriting the only source or releasing a corrected package without a clean-import regression test

## Handoff

Escalate to project survey and VDC authority when the coordinate basis, transformation lineage, independent control, vertical datum, model identity, or installed-work exposure cannot be proven; include design authority when semantic geometry or design revision is disputed.


Release rule: Release only when source identity, complete transform metadata, asymmetric 3D controls, independent design dimensions, vertical datum, required geometry, and clean-import regression all pass the project tolerance and the affected-work interval is bounded.

This card does not release the work.
