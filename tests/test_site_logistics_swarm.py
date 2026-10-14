from __future__ import annotations
from pathlib import Path
import yaml
from modules.site_logistics_swarm.swarm import SiteLogisticsSwarm
from modules.site_logistics_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "site-logistics" / "fixtures"

def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())

def test_lists_workflows():
    assert set(SiteLogisticsSwarm().list_workflows()) == set(WORKFLOW_IDS)

def test_pre_delivery_go():
    assert SiteLogisticsSwarm().run("pre-delivery-gate", _load("pre_delivery_go.yaml")).decision == "GO"

def test_floor_overload_abort():
    assert SiteLogisticsSwarm().run("floor-load-gate", _load("floor_overload_abort.yaml")).decision == "ABORT"

def test_aisle_blocked_abort():
    assert SiteLogisticsSwarm().run("laydown-aisle-gate", _load("aisle_blocked_abort.yaml")).decision == "ABORT"

def test_crane_swing_abort():
    assert SiteLogisticsSwarm().run("crane-drop-gate", _load("crane_swing_abort.yaml")).decision == "ABORT"

def test_temp_power_abort():
    assert SiteLogisticsSwarm().run("temp-utilities-gate", _load("temp_power_abort.yaml")).decision == "ABORT"

def test_window_hold():
    assert SiteLogisticsSwarm().run("access-window-gate", _load("window_hold.yaml")).decision == "HOLD"

def test_untagged_hold():
    assert SiteLogisticsSwarm().run("jit-inventory-gate", _load("untagged_hold.yaml")).decision == "HOLD"

def test_housekeeping_go():
    assert SiteLogisticsSwarm().run("end-of-day-housekeeping", _load("pre_delivery_go.yaml")).decision == "GO"

def test_hold_abort():
    assert SiteLogisticsSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "overload"}).decision == "ABORT"
