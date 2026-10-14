# AHJ inspection types

Source: `InspectionType` in `permit_inspection_service.py`.

foundation, footing, slab, framing, rough_electrical, rough_plumbing, rough_mechanical, fire_sprinkler, insulation, drywall, final_electrical, final_plumbing, final_mechanical, fire_alarm, fire_final, building_final, elevator, accessibility, energy_compliance.

Results: scheduled, in_progress, passed, passed_with_notes, failed, canceled, rescheduled.

Passed with notes still carries the notes. Do not drop them.
