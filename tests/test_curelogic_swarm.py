from __future__ import annotations
from pathlib import Path
import yaml
from modules.curelogic_swarm.swarm import CureLogicSwarm
from modules.curelogic_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "curelogic" / "fixtures"

def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())

def test_lists_workflows():
    assert set(CureLogicSwarm().list_workflows()) == set(WORKFLOW_IDS)

def test_pre_cure_go():
    assert CureLogicSwarm().run("pre-cure-gate", _load("pre_cure_go.yaml")).decision == "GO"

def test_evap_critical_abort():
    assert CureLogicSwarm().run("evaporation-gate", _load("evap_critical_abort.yaml")).decision == "ABORT"

def test_thermal_delta_abort():
    assert CureLogicSwarm().run("thermal-envelope-gate", _load("thermal_delta_abort.yaml")).decision == "ABORT"

def test_early_release_abort():
    assert CureLogicSwarm().run("day-n-maturity-gate", _load("early_release_abort.yaml")).decision == "ABORT"

def test_membrane_hold():
    assert CureLogicSwarm().run("membrane-cure-gate", _load("membrane_unlogged_hold.yaml")).decision == "HOLD"

def test_cold_unprotected_abort():
    assert CureLogicSwarm().run("cold-weather-cure-gate", _load("cold_unprotected_abort.yaml")).decision == "ABORT"

def test_dry_ambient_hold():
    assert CureLogicSwarm().run("pre-cure-gate", _load("dry_ambient_hold.yaml")).decision == "HOLD"

def test_closeout_go():
    assert CureLogicSwarm().run("curing-closeout", _load("pre_cure_go.yaml")).decision == "GO"

def test_hold_abort():
    assert CureLogicSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "freeze"}).decision == "ABORT"
