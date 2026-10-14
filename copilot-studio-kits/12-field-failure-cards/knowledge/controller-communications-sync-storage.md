# Total Station Controller, Communications, Power, Firmware, Native Storage, and Cloud Sync Failures

Source file: `controller_communications_sync_storage_failures_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** RAG dataset for field AI agents diagnosing total-station controller and robotic-link failures while preserving native evidence, data lineage, revision identity, and installed-work safety.

**Authority:** Manufacturer instructions, project data-governance rules, survey lead authority, IT/cloud administration, licensing terms, and authorized service procedures govern. Preserve native evidence and both sides of every conflict before recovery.

Record count in the source file: 64. Do not quote those records as this job.

## Out of this card

- Site control, coordinate-system design, occupied-point setup, resection geometry, pole/prism or backsight-tripod setup, tracking/search geometry, stakeout sign interpretation, CAD/BIM transforms, and internal instrument calibration except as independent checks
- Unauthorized device disassembly, sealed radio repair, battery-cell rebuilding, firmware bypass, license circumvention, cloud deletion, or destructive recovery on the only native copy

## When this shows up

- **No radio connection**
  Check first: instrument remote-wait state; instrument/controller serial; channel; network ID; internal/external radio path.
- **Radio repeatedly reconnects**
  Check first: battery state; module detection/contact; short-range swap test; site interference; line of sight.
- **Works near instrument, fails at layout range**
  Check first: active Bluetooth versus long-range transport; antenna/path obstruction; radio module; channel congestion.
- **Bluetooth device not visible**
  Check first: OS radio; location/nearby permission; discoverable state; correct device role; hardware comparison.
- **Instrument Wi-Fi works but internet does not**
  Check first: active single Wi-Fi association; cellular/SIM; Bluetooth tether; browser test; defer sync.
- **Job fails after battery event**
  Check first: preserve original; outage timestamp; last native record; repair duplicate; affected observation interval.
- **Points appear stored but export is short**
  Check first: Review job; raw observation; active job; free storage; export filter/record class.
- **Sync is green but file is missing**
  Check first: per-file status; conflict; role/assignment; route; hash/revision destination readback.
- **Same-name files disagree**
  Check first: hash; revision ID; coordinate metadata; common ancestor; approved cutover.
- **Failure started after update**
  Check first: OS/Access/firmware/module versions; permissions; driver/service package; license; known-good matrix.

## Do this

- Classify the first failing layer: power/hardware, OS/permission/driver, transport identity/configuration, survey session, native job, export, cloud revision/role, or destination verification.
- Preserve all evidence and both file revisions before any reset, reinstall, repair, cache deletion, or override.
- Use the fastest discriminating test and change only one layer while holding geometry and content fixed.
- After technical recovery, verify survey setup, native storage, file/revision lineage, destination readback, and installed-work exposure.

## Never do

- Deleting or overwriting the only native job, log set, cache, pairing evidence, local file, cloud file, or conflict copy
- Factory reset, reinstall, firmware retry, license bypass, or conflict override without a verified backup and documented recovery authority
- Continuing layout because communications automatically reconnected or sync displayed completion
- Using a coordinate-only export as replacement for raw/native observations and setup metadata
- Changing project control or design to absorb missing, shifted, or stale data

## Handoff

Escalate to the survey lead plus the appropriate dealer, IT/cloud administrator, or license administrator when hardware swaps carry the fault, firmware recovery is required, jobs need repair, entitlement/roles block work, versions conflict, data is missing, or installed work may be affected.


Release rule: Release only when the exact endpoint/link is stable, survey state passes control, the native observation survives reopen, all dependencies and revisions match the approved manifest, destination readback passes, and affected work is dispositioned.

This card does not release the work.
