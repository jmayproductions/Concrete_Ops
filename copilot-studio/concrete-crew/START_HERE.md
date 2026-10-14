# START HERE — Drop-in for work tomorrow

This folder is a **ready Copilot Studio agent workspace**.

## 3 steps (≈10 minutes)

### 1) Open in VS Code
- Install **Microsoft Copilot Studio** VS Code extension (sign in to your work tenant / environment).
- **File → Open Folder** → select this `concrete-crew` folder (the one that contains `agent.mcs.yml`).

### 2) Push to your environment
Recommended safe path if the extension expects an existing cloud agent:

1. In Copilot Studio web: **Create** a blank agent named `ConcreteOps Crew Swarm`.
2. In VS Code Copilot Studio panel: **Clone agent** into a temp folder.
3. Copy **everything from this drop-in** over the clone (keep the clone’s `schemaName` in `settings.mcs.yml` if Studio already assigned one).
4. **Push** / sync from VS Code.

If your work environment allows push-from-local without clone, open this folder and push directly.

### 3) Attach knowledge (after children exist)
1. Push parent + `agents/*` child agents first.
2. Then upload files from `knowledge/files/` as knowledge sources (workflows + specialists).
3. Test a starter: *“Run pre-pour-gate for today's deck pour…”*

## What’s inside

| Path | Purpose |
| --- | --- |
| `agent.mcs.yml` | Parent orchestrator |
| `settings.mcs.yml` | Generative orchestration **ON** |
| `agents/*/agent.mcs.yml` | 14 child specialists |
| `topics/Greeting.topic.mcs.yml` | Conversation start |
| `knowledge/files/` | Playbooks to attach as knowledge |
| `samples/` | Example pour context JSON for tests |

## Optional backend (later)
Deterministic twin for Power Automate / custom connector lives in the repo:
`python -m modules.agent_swarm.api --port 8080`

You do **not** need it for tomorrow’s Studio bring-up.

## Do not edit
- After first cloud sync, prefer the Studio-assigned `schemaName` in `settings.mcs.yml`.
- Do not invent new child agents in chat — only the 14 under `agents/`.
