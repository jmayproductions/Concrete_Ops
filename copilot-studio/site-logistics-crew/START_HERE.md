# START HERE — Site Logistics Swarm drop-in

Ready Copilot Studio workspace for delivery, laydown, and temp-utility field gates.

## 3 steps
1. Open this `site-logistics-crew` folder in VS Code with Copilot Studio extension.
2. Create blank agent **Site Logistics Swarm** → Clone → overwrite with this pack (keep Studio `schemaName`) → Push.
3. Attach `knowledge/files/` → test *“Run pre-delivery-gate…”*.

## Workflows
`pre-delivery-gate`, `access-window-gate`, `laydown-aisle-gate`, `floor-load-gate`, `material-move-gate`, `lift-path-gate`, `crane-drop-gate`, `temp-utilities-gate`, `traffic-control-gate`, `jit-inventory-gate`, `end-of-day-housekeeping`, `hold-abort`

## Optional backend
```bash
python -m modules.site_logistics_swarm.api --port 8101
python -m modules.site_logistics_swarm.cli run pre-delivery-gate -c agents/site-logistics/fixtures/pre_delivery_go.yaml
```
