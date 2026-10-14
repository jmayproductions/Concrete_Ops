# Commissioning Swarm (reference twin)

> See [`../../copilot-studio/commissioning-crew/`](../../copilot-studio/commissioning-crew/) → `START_HERE.md`.

```bash
python -m modules.commissioning_swarm.cli list
python -m modules.commissioning_swarm.cli run pre-cx-gate -c agents/commissioning/fixtures/pre_cx_go.yaml
python -m modules.commissioning_swarm.api --port 8102
```
