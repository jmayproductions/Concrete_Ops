# Pour lifecycle (template)

States used by StructureOps `pour_controller.py`:

1. initialized
2. precheck_pending
3. precheck_failed
4. approved (human / engineer — not this agent)
5. in_progress
6. paused
7. completed
8. failed
9. cancelled

This agent can help with precheck. It cannot move a pour to **approved**.

Template pour config (override from spec):

- min crew size: 4
- max duration: 8 hours
- temp: 40–90°F
- max wind: 25 mph
- certifications often required: ACI, OSHA
- weekend pours: not assumed allowed
- engineer approval: required unless the user says the project does not require it
