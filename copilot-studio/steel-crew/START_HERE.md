# START HERE — Structural Steel Erection Swarm drop-in

This folder is a **ready Copilot Studio agent workspace** for field steel erection.

## Sources
Project `construction.md` steel erection / steel construction QA extracts (AISC, RCSC, AWS D1.1). See `knowledge/files/SOURCES.md`.

## 3 steps

### 1) Open in VS Code
- Install **Microsoft Copilot Studio** VS Code extension (sign in to your work tenant).
- **File → Open Folder** → select this `steel-crew` folder (contains `agent.mcs.yml`).

### 2) Push to your environment
1. In Copilot Studio web: **Create** a blank agent named `Structural Steel Erection Swarm`.
2. In VS Code: **Clone agent** into a temp folder.
3. Copy **everything from this drop-in** over the clone (keep Studio `schemaName` if already assigned).
4. **Push** / sync.

### 3) Attach knowledge
1. Push parent + `agents/*` first.
2. Upload `knowledge/files/` as knowledge sources.
3. Test: *“Run pre-erect-gate for Level 5 Grid A-D…”*

## Named workflows
`pre-erect-gate`, `delivery-piece-gate`, `anchor-baseplate-gate`, `level-erect-runbook`, `column-beam-pick`, `bolting-qa`, `welding-ndt-gate`, `bracing-stability-lock`, `plumb-alignment-check`, `decking-release`, `level-closeout`, `hold-abort`

## Optional backend
```bash
python -m modules.steel_swarm.api --port 8082
python -m modules.steel_swarm.cli run pre-erect-gate -c agents/steel/fixtures/pre_erect_go.yaml
```
