# Install a kit in Copilot Studio

Source mapping: `microsoft-365-docs-public/copilot/agent-essentials`.

Admin roles that may be required: Copilot administrator, Power Platform administrator, SharePoint administrator, Microsoft 365 Search administrator.

## 1. Choose the Studio experience

| Need | Use |
|---|---|
| Instructions + SharePoint / uploaded files + no custom actions | Agent Builder (declarative agent) |
| Topics, tools, other agents, autonomous triggers | Copilot Studio custom agent |
| ZIP for admin upload / sideload | Either — download ZIP after publish |

Kits 01 and 03 work in Agent Builder. Kits 02, 04, 05, and 06 through 12 need Copilot Studio topics (and optionally child agents).

## 2. Create the agent

1. Open Copilot Studio in the work tenant.
2. Create a new agent.
3. Paste `description.md` into the description field.
4. Paste `instructions.md` into Instructions. Then append every file in `skills/` that the kit README marks as **instruction-level**.
5. Upload every file listed under `knowledge` in `kit.yaml`.
6. For each file in `topics/`, create a topic: copy trigger phrases, then paste the response contract into the topic message / generative answers node.
7. Add tools from `tools.md`. Enable only connectors the work tenant already allows.
8. Attach SharePoint / OneDrive knowledge for **this job** after legal/IT review. Do not bulk-copy this repo.

## 3. Test with the kit prompts

Run `test-prompts.md` in Test your agent. Confirm:

- Missing evidence produces a refusal phrase, not a made-up drawing number
- Drafts are labeled DRAFT
- Submittal notes never say approved or rejected
- Quantities, dates, costs, and schedule impacts are UNKNOWN unless a cited source states them

## 4. Publish and export the ZIP

1. Publish the agent.
2. **Agents → [name] → Channels → Teams and Microsoft 365 Copilot**.
3. **Availability options → Download .zip**.
4. In Microsoft 365 admin center: **Copilot Control System → Agents → Upload custom agent**.
5. Assign **Just me** or one test group first.
6. Review permissions, then finish deployment.

Agent Builder also has **Download agent ZIP file and provide to admin**.

## 5. Knowledge and oversharing

The agent only sees files the signed-in user can open. Before attaching a project library:

- Confirm site permissions are not overshared
- Prefer a dedicated PE / estimating site with a closed membership
- Keep sensitivity labels on drawings and contracts
- Leave demo fixtures out of the work knowledge set

## 6. Suggested first rollout

1. Daily PE Copilot (kit 01) against one closed SharePoint PE site, using `01-daily-pe-copilot/tools/sharepoint-library-read.md`. Add the Autodesk issue and RFI read contracts only after IT approves a 3-legged app with `data:read` and no write scope.
2. Document-control clerk (kit 06) on the same PE site, as topics or a child agent. Sheet and file questions use `06-document-control-clerk/tools/autodesk-sheet-file-read.md` on the same read-only app. A Docs tip version is not the current revision by itself.
3. PE document drafter (kit 02) as topics on the same agent **or** a child agent, including the NCR topic. Submittal questions use `02-pe-document-drafter/tools/autodesk-submittal-read.md` on the same read-only Autodesk app. The drafter still does not approve the package.
4. Estimating coach (kit 03) for preconstruction, separate agent
5. Concrete field QA (kit 04) for field / superintendent users
6. Trade/role shells (kit 05) only after 01–04 are stable
7. AHJ permit tracker (kit 07), closeout pack (kit 08), and procurement (kit 09) when those logs exist in SharePoint
8. Tilt-up field QA (kit 10) for tilt-up work, beside concrete field QA
9. Safety and JHA (kit 11) for field leads, beside the kit 05 safety shell. Upload company JHAs and the federal pamphlets in `11-safety-jha/knowledge/pamphlet-index.md`. Do not attach a tool that files an OSHA log.
10. Field failure cards (kit 12) when someone is troubleshooting a symptom. Upload the markdown cards only. Leave the JSON issue files in `S:\Swinerton\KBs`.
