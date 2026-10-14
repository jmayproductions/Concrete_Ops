# Kit 04 — Concrete field QA

For field and superintendent users. Keep it off the estimating agent.

Checklist knowledge is copied from `modules/field_ops/qaqc_engine.py` and pour gates from `pour_controller.py`. Live pour state, clock-in, and weather APIs stay in StructureOps unless a connector is approved.

## Success check

"We're at 38°F. Are we good to pour?"

**Pass:** Weather gate fails (template min 40°F). Does not authorize. Asks for spec cold-weather procedure and whether the engineer waived anything in writing.
