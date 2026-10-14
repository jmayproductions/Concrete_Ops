# Construction Copilot agent swarm

Parent + children built from the kits in this package. Author in Copilot Studio, then use the established **build → publish → Download .zip → admin upload** loop ([INSTALL.md](INSTALL.md)).

## Topology

```text
                    ┌─────────────────────────┐
                    │  01 Daily PE Copilot    │  parent / classifier
                    │  (evidence-gated)       │
                    └───────────┬─────────────┘
          ┌─────────────┬───────┼───────┬─────────────┬──────────┐
          ▼             ▼       ▼       ▼             ▼          ▼
   06 Doc control   02 Drafter  07 AHJ  09 Buyout   05 Shells   12 Failure
          │             │                              │          cards
          │             ▼                              ├─ safety → 11 JHA
          │        08 Closeout                         ├─ concrete → 04 QA
          │                                            ├─ tilt → 10 QA
          │                                            └─ steel/elec/plumb/wx/sched
          │
   03 Estimating (separate agent — preconstruction lane)
```

## Handoff rules (from kit 05)

1. User asks in Microsoft 365 Copilot / Teams.
2. Parent (01) classifies the lane (`knowledge/pe-lanes.md` + intent map).
3. Hand off or switch topic to the matching child.
4. Child answers in its lens; lists what it cannot decide.
5. Parent restates Evidence, Confidence, and next PE action.

Safety-critical “is it safe to…” stays **BLOCKED** — route to a human.

## Rollout order (same as INSTALL)

1. 01 + SharePoint PE site  
2. 06 on same agent or child  
3. 02 (incl. NCR)  
4. 03 estimating (separate)  
5. 04 concrete QA  
6. 05 shells  
7. 07 / 08 / 09 when logs exist  
8. 10 tilt-up beside 04  
9. 11 safety beside 05  
10. 12 failure cards for symptom triage  

## Studio → zip → download (repeatable)

For **each** agent (or parent with children):

1. Paste `description.md` + `instructions.md` + instruction-level skills.
2. Upload knowledge listed in `kit.yaml` (plus `_shared` files).
3. Create topics from `topics/`.
4. Enable only approved tools from `tools.md`.
5. Run `test-prompts.md`.
6. **Publish**.
7. **Channels → Teams and Microsoft 365 Copilot → Availability options → Download .zip**.
8. M365 admin: **Copilot Control System → Agents → Upload custom agent**.
9. Assign Just me / one test group first.

Authoring kits here are **not** the Studio ZIP. The ZIP is what Studio emits after publish.

## RAG JSON vs Studio knowledge

- Upload **kit markdown** (especially kit 12 cards) into Copilot Studio knowledge.
- Keep full `*_failures_rag_v1.json` (2,209 issues) for retrieval backends / MCP / custom connectors — see [AGENT_DATA_INDEX.md](AGENT_DATA_INDEX.md).
- Do not treat forum/incident RAG sources as pour/lift/occupancy approval authority.
