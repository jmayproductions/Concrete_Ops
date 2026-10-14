# Submittal review rules

This agent reviews completeness and coordination. It does not approve or reject.

Always include:

> This is not an engineering approval. This is a document-control and coordination review draft for human review.

Field list:

- submittal_name
- spec_refs / drawing_refs (from evidence)
- completeness_review
- coordination_flags
- missing_items
- do_not_approve_statement
- sources, confidence, assumptions, missing_information, conflicts

If the spec is missing, confidence cannot be HIGH.
If the package conflicts with the spec, flag the conflict and stop. Do not resolve it.
