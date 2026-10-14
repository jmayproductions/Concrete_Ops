# Suggested tools — Document-control clerk

| Tool | Use | Write? |
|---|---|---|
| SharePoint / OneDrive | Drawing log, specs, transmittal folder | Read |
| File upload | A sheet or stamp the user drops in | Read |
| Excel / SharePoint list | Propose a revision-log row or transmittal row | Write — confirm |
| Word | Transmittal cover draft | Write — confirm |
| Outlook draft | Cover email | Write — confirm, never send |

Do not connect a file-distribution connector that sends to the whole project team.

## Read contract

| Contract | File | Write? |
|---|---|---|
| Autodesk sheets and Docs files | `tools/autodesk-sheet-file-read.md` | Read |

Enable it on the same 3-legged app as kit 01, with `data:read` and `account:read`. Do not request `data:write`. Publishing sheets and uploading files are out.
