# StructureOps Copilot Studio Agent Kits

PE, field QA, closeout, and buyout kits for a work Copilot Studio tenant. Built from StructureOps doctrine.

These files are **authoring kits**, not a Copilot Studio ZIP. You paste them into Copilot Studio, then download the ZIP from **Channels → Teams and Microsoft 365 Copilot → Availability options → Download .zip** and upload that ZIP in the Microsoft 365 admin center.

## Kits

| Folder | Agent | Studio shape | Status |
|---|---|---|---|
| [01-daily-pe-copilot](01-daily-pe-copilot/) | Daily PE Copilot | Declarative / Agent Builder or Copilot Studio instructions | Author first |
| [02-pe-document-drafter](02-pe-document-drafter/) | PE document drafter | Copilot Studio topics (11 workflows, including NCR) | Author second |
| [03-estimating-coach](03-estimating-coach/) | Estimating coach | Instructions + knowledge files | Author third |
| [04-concrete-field-qa](04-concrete-field-qa/) | Concrete field QA | Knowledge + five checklist topics | Author fourth |
| [05-trade-role-shells](05-trade-role-shells/) | Trade and role shells | Child agents / handoff topics | Instruction shells only |
| [06-document-control-clerk](06-document-control-clerk/) | Document-control clerk | Topics for revision, transmittal, conflict | Author with kit 01 |
| [07-ahj-permit-tracker](07-ahj-permit-tracker/) | AHJ permit tracker | Permit, inspection, correction topics | After kit 01 |
| [08-closeout-pack](08-closeout-pack/) | Closeout pack | Commissioning, warranty, gap list | After kit 02 |
| [09-procurement-long-lead](09-procurement-long-lead/) | Procurement and long-lead | Requisition and delivery topics | After kit 01 |
| [10-tilt-up-field-qa](10-tilt-up-field-qa/) | Tilt-up field QA | Panel phase checklists | With kit 04 |
| [11-safety-jha](11-safety-jha/) | Safety and JHA | JHA, toolbox talk, incident note | After kit 05 |
| [12-field-failure-cards](12-field-failure-cards/) | Field failure cards | Symptom router, never-do, handoff | Beside 04, 05, 10, 11 |

Shared law used by every kit lives in [_shared/](_shared/).

## How a kit is laid out

```text
NN-kit-name/
  README.md           How to stand this agent up
  kit.yaml            Manifest: name, knowledge, topics, tools
  instructions.md     Paste into Copilot Studio Instructions
  description.md      Short agent description for the catalog
  tools.md            Suggested Copilot Studio tools and connectors
  skills/*.md         One skill per file — paste as instructions or topics
  topics/*.md         Conversation topics (trigger phrases + response contract)
  knowledge/*.md      Upload as knowledge files
  workflows/*.md      Operator workflows (when to use which topic)
  test-prompts.md     Pilot prompts for the work tenant
```

## What to upload as knowledge

Upload the kit `knowledge/` files plus `_shared/` files listed in that kit's `kit.yaml`.

Do **not** upload:

- Project drawings or specs from this repo's demo workspace
- `backend/generated_docs/` sample daily reports
- v2 sample schedule rows or pour names
- Client documents that have not been reviewed for the work tenant

Real job documents go in the work tenant's SharePoint or OneDrive libraries. The signed-in user must already have permission to those files.

## What stays in StructureOps

Local retrieval, Ollama, BIM/survey validators, takeoff geometry, vision, FastAPI, and the v2 TypeScript runner. Those become Copilot Studio tools only after a hosted connector the work tenant is allowed to call.

## Agent data + swarm

- [AGENT_DATA_INDEX.md](AGENT_DATA_INDEX.md) — RAG corpora, SOPs, Drive links
- [SWARM.md](SWARM.md) — parent/child topology and handoffs

## Install

See [INSTALL.md](INSTALL.md).
