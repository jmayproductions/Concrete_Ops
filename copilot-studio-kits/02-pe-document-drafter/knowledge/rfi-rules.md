# RFI draft rules

Draft an RFI when:

- Drawing detail is unclear or a dimension is missing
- Spec is ambiguous about a product, method, or standard
- Documents conflict
- Field condition differs from drawing/spec
- Trades clash and the drawings do not resolve it
- A submittal or buyout is blocked by missing information
- Closeout requirement is unclear
- User asks for an RFI

Field list:

- status: DRAFT | BLOCKED | READY_FOR_REVIEW
- title
- question (specific and answerable)
- background
- drawing_or_spec_refs (from evidence only)
- field_condition
- proposed_solution_if_any (empty unless user or source offers one)
- schedule_impact / cost_impact: UNKNOWN unless sourced
- needed_by (empty unless sourced)
- sources, confidence, assumptions, missing_information, conflicts

The question must be specific. Not “clarify concrete.” Yes: “Spec section [cited] requires admixture submittals; drawing note [cited] says see manufacturer. Which controls?”
