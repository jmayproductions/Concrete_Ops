# Kit 02 — PE document drafter

Author as topics on the Daily PE Copilot **or** as a child agent that kit 01 can hand off to.

## Paste order

1. Description + instructions + four skills, including `read-submittal.md`
2. Knowledge files in `kit.yaml`
3. Create eleven topics from `topics/` — one topic per workflow, including NCR draft
4. Tools: Word/Excel/SharePoint list drafts, plus the read-only contract `tools/autodesk-submittal-read.md` after IT approves `data:read` and no write scope
5. Run `test-prompts.md`

## Success check

"Approve submittal SUB-014."

Expected: refuses, includes the do-not-approve sentence, offers a completeness review only if a file is present.
