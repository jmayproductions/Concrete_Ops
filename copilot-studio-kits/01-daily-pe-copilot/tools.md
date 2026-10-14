# Suggested tools — Daily PE Copilot

Enable the minimum set. Writes need a human confirmation in Copilot Studio.

## Enable now

| Tool | Use | Write? |
|---|---|---|
| SharePoint / OneDrive search | Find current specs, drawings, logs | Read |
| Microsoft 365 Copilot file upload | User drops a PDF/DOCX/XLSX into chat | Read |
| Word create document | Save a DRAFT RFI or meeting note | Write — confirm |
| Excel create / update | Append a row to an RFI or submittal log sheet | Write — confirm |

## Enable after a closed PE site exists

| Tool | Use | Write? |
|---|---|---|
| SharePoint list (RFI log, submittal log, constraint log) | Read status; propose a new item | Write — confirm |
| Outlook draft | Draft an RFI email to the design team | Write — confirm, never auto-send |
| Teams draft message | Talking points for OAC | Write — confirm |
| Planner / To Do | Turn a recommended action into a task | Write — confirm |

## Read contracts

These are the first two pipes. Full contracts are in `tools/`.

| Contract | File | Write? |
|---|---|---|
| One SharePoint PE library | `tools/sharepoint-library-read.md` | Read |
| Autodesk issue | `tools/autodesk-issue-read.md` | Read |
| Autodesk RFI | `tools/autodesk-rfi-read.md` | Read. Search is a POST with an empty or filter body. It must not create an RFI. |

Enable the Autodesk reads only after IT approves a 3-legged app with `data:read` and `account:read`. Do not request `data:write`.

## Do not enable on this agent

- Public web search as a source of project facts
- Any StructureOps localhost or unhosted API
- Calendar "schedule inspection" without a human
- Any connector that can create, close, or edit an Autodesk issue or RFI
- The vendored ACC bulk uploader. It moves files. It is not this read contract.
