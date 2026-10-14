# How these files map to Copilot Studio

| Kit file | Copilot Studio control |
|---|---|
| `instructions.md` + instruction-level `skills/` | Agent **Instructions** |
| `description.md` | Agent name / description |
| `knowledge/*.md` and `_shared/*.md` | **Knowledge** — upload files |
| SharePoint PE / estimate / field libraries | **Knowledge** — SharePoint |
| `topics/*.md` | **Topics** — trigger phrases + message |
| `tools.md` | **Tools** — Office 365, SharePoint, Power Automate, custom connectors |
| `workflows/*.md` | Operator runbook, or Power Automate later |
| Child agents in kit 05 | **Add other agents** |
| Published ZIP | Admin **Upload custom agent** |

## Suggested Microsoft 365 tools (enable only if the tenant allows them)

- SharePoint / OneDrive file search
- Outlook (draft only — never send without confirmation)
- Teams (post only with confirmation)
- Word / Excel create-document (drafts)
- Planner or To Do (action items, with confirmation)
- Power Automate (RFI log / submittal log updates)

## Do not enable by default

- Send email
- Create calendar events that look like inspections
- Any connector to an unhosted StructureOps API
- Public web search for project facts (web search may be used only when labeled as general knowledge)
