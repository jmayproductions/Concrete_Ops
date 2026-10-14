# Kit 06 — Document-control clerk

Author after Daily PE Copilot. It can be a child agent or a set of topics on the same PE agent.

## Paste order

1. Description + instructions + four skills, including `read-sheet-set.md`
2. Knowledge files in `kit.yaml`
3. Four topics
4. SharePoint drawing log and specs as knowledge (the job’s own library)
5. After IT approves `data:read` and no write scope, add `tools/autodesk-sheet-file-read.md`
6. Run `test-prompts.md`

## Success check

"Rev C is newer, so use Rev C."

Expected: refuses to treat a later letter as current until a log, transmittal, or issuance record says Rev C is the approved current revision.
