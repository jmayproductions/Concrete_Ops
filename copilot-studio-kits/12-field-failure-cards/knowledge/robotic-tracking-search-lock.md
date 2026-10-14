# Common Robotic Total-Station Tracking, Search, Reacquisition, and Wrong-Target Lock Failures

Source file: `robotic_tracking_search_lock_failures_rag_v1.json` in `S:\Swinerton\KBs`.
Issue records stay in that file. This card is the router, the never-do list, and the handoff.

**Use:** Retrieval dataset for field AI agents diagnosing robotic interaction failures between a total station, controller, target, environment, and storage workflow.

**Authority:** Project specifications, current equipment manuals, the survey lead, calibration authority, and site-control governance supersede this dataset. Agents must stop and prove target identity before recommending continued layout.

Record count in the source file: 64. Do not quote those records as this job.

## Out of this card

- Physical layout-pole tip, locks, height, bubble, bend, bipod, and point-contact failures
- Dedicated backsight tripod, tribrach, carrier, height, prism mechanics, and control-point failures
- Occupied total-station tripod, centering, instrument height, compensator, physical settlement, and non-robotic axis failures except tracker-specific calibration
- Project-control, station, localization, or design changes used as prohibited masking actions

## When this shows up

- **Robot follows motion but deltas do not match pole**
  Check first: vest or operator lock; another crew prism; target ID; full occlusion.
- **Discrete jump after obstruction**
  Check first: different prism reacquired; 360 sector change; prediction interval; search behavior; ID recheck.
- **Lock fails after reconnect or job change**
  Check first: target number; target type; active/passive mode; ID policy; power; instrument compatibility.
- **Search repeatedly turns to wrong area**
  Check first: fixed region; last pointing direction; GeoLock GNSS; search window; camera alignment.
- **Short-range switching between prisms**
  Check first: FineLock aperture; angular separation; snap-to-target; one-target isolation.
- **Long-range close targets switch**
  Check first: LR FineLock; angular separation; target ID; distance verification.
- **Horizontal seems correct but elevation jumps**
  Check first: passive vertical lock interference; reflective surface; 360 face; active/semi-active mode; vertical angle.
- **Manual pointing passes; automatic aim fails**
  Check first: ATR/Autolock collimation; sensor contamination; servo; camera; firmware or service state.
- **Stored point differs from last live position**
  Check first: lock lost during measure; automatic search-on-measure; unexpected second shot; tracking versus precision mode.
- **Failures correlate with glass, traffic, or PPE**
  Check first: passive false lock; snap-to-target; identity policy; search region; active target.

## Do this

- Confirm the failure is robotic interaction rather than physical pole, backsight, or occupied-station hardware.
- Classify the signature as false identity, mode/configuration, search/reacquisition, obstruction/clutter, geometry, tracker calibration, connection/storage, or recovery failure.
- Preserve native automation metadata and isolate one robotic layer at a time.
- Stop and conservatively bound work whenever identity is uncertain.
- Require correct-target acceptance, competing-target rejection, and an independent known-point check before release.

## Never do

- Trusting a lock icon or successful distance result as sufficient target identity
- Averaging through wrong-target jumps, mixed reflections, lock loss, or sector changes
- Changing control, station, localization, calibration, or design data to absorb a robotic identity fault
- Continuing production after reacquisition without proving the same physical target was recovered

## Handoff

Escalate when identity features, target compatibility, tracker calibration, instrument hardware, controller state, or the affected installed-work interval cannot be proven.


Release rule: Resume only after identity, rejection of competing targets, reacquisition behavior, precision storage, and an independent known point all pass and the affected interval is bounded.

This card does not release the work.
