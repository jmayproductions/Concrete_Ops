# Construction Layout QA/QC, As-Built Verification, Tolerance, NCR, and Turnover Failures

Source file: `layout_qaqc_asbuilt_verification_failures_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** RAG dataset for field AI agents preventing unverified construction layout, tolerance misuse, incomplete as-builts, weak deviation investigations, revision-driven rework, undocumented acceptance, and unusable turnover records.

**Authority:** The executed contract, current issued documents, adopted standard edition, project specifications, approved submittals/RFIs, quality plan, licensed professionals, owner/designer authority, and jurisdiction govern. Example tolerances in sources must never be substituted for project requirements.

Record count in the source file: 64. Do not quote those records as this job.

## Out of this card

- Primary control-network design, occupied-point/resection computation, pole/prism and backsight hardware, robotic tracking, stakeout sign/UI, CAD/BIM coordinate transformation, instrument calibration, and controller communications except when required to preserve QA evidence or route the fault
- Legal allocation of liability, professional engineering decisions, contract interpretation by unauthorized agents, destructive repairs, or acceptance of nonconforming structural/life-safety work without designated authority

## When this shows up

- **Backsight closes but independent point fails**
  Check first: third-point lineage; check geometry; setup/control error; target metadata; orientation dependence.
- **Morning checks pass and afternoon work trends**
  Check first: same unadjusted check; tripod/control disturbance; temperature/load; event timeline; affected interval.
- **Software says green but inspector rejects**
  Check first: governing specification; active tolerance profile; datum/frame; asymmetric sign; method uncertainty.
- **As-built is near zero but another crew finds a shift**
  Check first: shared setup/control/file; independent method; design revision; source-coordinate edit; wrong feature identity.
- **Vertical passes and horizontal fails**
  Check first: feature reference and stake note; center/face/curb definition; 3D as-built coverage; point/model identity; installation movement.
- **Anchor group center passes but steel will not fit**
  Check first: individual bolt pattern; rotation; spacing; projection/elevation; approved shop geometry.
- **Two instruments or methods disagree**
  Check first: same datum/point/state; known-reference test; full precision; uncertainty; contract-required method.
- **Field matches old model**
  Check first: actual device/print revision; issued register; RFI/submittal incorporation; field acknowledgment; cutover timestamp.
- **Issue closed but no acceptance measurement**
  Check first: post-correction native observation; independent setup; tolerance calculation; reviewer signature; downstream release.
- **Turnover files disagree**
  Check first: immutable feature IDs; redline/model/sheet reconciliation; exception register; hash/version; decision links.

## Do this

- Identify the governing feature, design/decision revision, reference frame, construction state, tolerance authority, and measurement capability.
- Preserve native observations, physical evidence, versions, and issue history; establish independent control/setup checks and remeasure without altering the condition.
- Separate observed deviation from root cause and responsibility; trace design, layout, mark, installation, movement, and acceptance events.
- Hold affected work and interfaces until authorized disposition, corrective action, independent final verification, and turnover reconciliation are complete.

## Never do

- Choosing a convenient tolerance, rounding rule, datum, sign, or model revision after seeing the measurements
- Deleting failed observations or modifying source coordinates/control to make historic QA records appear compliant
- Accepting critical work from the same setup/file/control path without an independent verification appropriate to risk
- Repairing, covering, loading, or connecting nonconforming work before preserving the original condition and obtaining authority
- Closing issues or delivering record models that omit exceptions, raw lineage, decision history, or coordinate-system metadata

## Handoff

Escalate to the survey/QC lead and designated designer, owner, inspector, or contract authority whenever tolerance basis is unclear, method uncertainty is inadequate, independent checks fail, revisions conflict, work is concealed/irreversible, deviations affect interfaces or safety, causation is disputed, or record evidence cannot be reproduced.


Release rule: Release only when design authority, tolerance, measurement capability, independent setup/control checks, final-state as-built coverage, raw lineage, exceptions/dispositions, corrective verification, affected-work review, and signed record handoff all pass.

This card does not release the work.
