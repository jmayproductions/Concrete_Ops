# Kit 01 — Daily PE Copilot

Stand this agent up first. It is the daily driver.

## Paste order

1. `description.md` → agent description
2. `_shared/ironclad-law.md` + `instructions.md` → Instructions
3. Every `skills/*.md` → append to Instructions, including `detect-conflicts.md` and `use-project-sources.md`
4. Knowledge files listed in `kit.yaml`, including `conflict-types.md`
5. Three topics from `topics/`, including Report a conflict
6. Tools from `tools.md`. Read contracts: `tools/sharepoint-library-read.md`, `tools/autodesk-issue-read.md`, `tools/autodesk-rfi-read.md`
7. Attach one work PE SharePoint site after review. Enable Autodesk reads only after IT approves a 3-legged app with `data:read` and no write scope.

## Success check

Ask: "What submittals does spec 03 30 00 require?" with no spec attached.

Expected: **Insufficient evidence**, confidence BLOCKED, next action = upload or point at the spec. Not a guessed CSI list.
