# START HERE — Mass Timber Sequencing Swarm drop-in

This folder is a **ready Copilot Studio agent workspace** for field engineered-wood erection.

## Sources
Scarlett WoodWorks mass timber construction slides (220310) + Mass Timber Design Manual (MTM_digital_final_033021). See `knowledge/files/SOURCES.md`.

## 3 steps

### 1) Open in VS Code
- Install **Microsoft Copilot Studio** VS Code extension (sign in to your work tenant / environment).
- **File → Open Folder** → select this `mass-timber-crew` folder (the one that contains `agent.mcs.yml`).

### 2) Push to your environment
Recommended safe path if the extension expects an existing cloud agent:

1. In Copilot Studio web: **Create** a blank agent named `Mass Timber Sequencing Swarm`.
2. In VS Code Copilot Studio panel: **Clone agent** into a temp folder.
3. Copy **everything from this drop-in** over the clone (keep the clone’s `schemaName` in `settings.mcs.yml` if Studio already assigned one).
4. **Push** / sync from VS Code.

If your work environment allows push-from-local without clone, open this folder and push directly.

### 3) Attach knowledge (after children exist)
1. Push parent + `agents/*` child agents first.
2. Then upload files from `knowledge/files/` as knowledge sources (SOPs + gate-order playbooks).
3. Test a starter: *“Run pre-erect-gate for Level 4 Zone A…”*

## What’s inside

| Path | Purpose |
| --- | --- |
| `agent.mcs.yml` | Parent orchestrator |
| `settings.mcs.yml` | Generative orchestration **ON** |
| `agents/*/agent.mcs.yml` | 16 erection specialists |
| `topics/Greeting.topic.mcs.yml` | Conversation start |
| `knowledge/files/` | Playbooks to attach as knowledge |
| `samples/` | Example erect context YAML for tests |

## Named workflows (ask the parent)
`pre-erect-gate`, `delivery-jit-gate`, `level-erect-runbook`, `panel-placement`, `glulam-frame-erect`, `bracing-diaphragm-lock`, `moisture-daily-check`, `connection-qa`, `hybrid-interface-gate`, `topping-release`, `level-closeout`, `hold-abort`

## Optional backend (later)
Deterministic twin for Power Automate / custom connector lives in the repo:

```bash
python -m modules.mass_timber_swarm.api --port 8081
python -m modules.mass_timber_swarm.cli run pre-erect-gate -c agents/mass-timber/fixtures/pre_erect_go.yaml
```

You do **not** need it for Studio bring-up.

## Do not edit
- After first cloud sync, prefer the Studio-assigned `schemaName` in `settings.mcs.yml`.
- Do not invent new child agents in chat — only the 16 under `agents/`.
