# NCR draft rules

Source: `backend/services/ncr_service.py`. This agent drafts the report. It does not open, assign, verify, or close an NCR in a system of record.

## Status the agent may write

DRAFT or BLOCKED only.

Lifecycle words (open, assigned, in progress, resolved, verified, closed, disputed) are for the human log. Do not set them unless the user is quoting a log that already says so.

## Fields

- location (zone, floor, grid) — from the user or a source
- description of what was seen or written
- severity: critical | major | minor | observation — only if the user or a source classifies it. Otherwise leave blank and list it under missing_information
- category: material | workmanship | dimension | safety | design_conflict | missing_work
- detected_by — only if named
- photo refs
- specification_ref and plan_sheet_ref — from evidence only
- assigned_to — empty unless a source names them
- root_cause, corrective_action, preventive_action — empty unless the user or a source states them
- sources, confidence, assumptions, missing_information

## Category limits

Do not use `code_violation`. A code conclusion is BLOCKED (`LEGAL_OR_CODE_AUTHORITY_REQUIRED`). Describe the condition and point at the spec or drawing.

Do not call a condition structurally inadequate. If the user says “this looks structural,” set severity only as the user’s words and flag ENGINEERING_JUDGMENT_REQUIRED. Recommend the engineer of record or special inspector.

## Template response windows

These hours come from the StructureOps service. They are templates, not this project’s contract SLA. Label them `[TEMPLATE]`.

| Severity | Template window |
|---|---|
| critical | 24 hours |
| major | 48 hours |
| minor | 72 hours |
| observation | 168 hours |

Do not invent an NCR number. The log assigns the number.
