from __future__ import annotations
from pathlib import Path
import yaml
from modules.commissioning_swarm.swarm import CommissioningSwarm
from modules.commissioning_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "commissioning" / "fixtures"

def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())

def test_lists_workflows():
    assert set(CommissioningSwarm().list_workflows()) == set(WORKFLOW_IDS)

def test_pre_cx_go():
    assert CommissioningSwarm().run("pre-cx-gate", _load("pre_cx_go.yaml")).decision == "GO"

def test_functional_go():
    assert CommissioningSwarm().run("functional-test-gate", _load("pre_cx_go.yaml")).decision == "GO"

def test_witness_missing_abort():
    assert CommissioningSwarm().run("functional-test-gate", _load("witness_missing_abort.yaml")).decision == "ABORT"

def test_deviation_abort():
    assert CommissioningSwarm().run("performance-gate", _load("deviation_abort.yaml")).decision == "ABORT"

def test_unsafe_startup_abort():
    assert CommissioningSwarm().run("startup-gate", _load("unsafe_startup_abort.yaml")).decision == "ABORT"

def test_life_safety_abort():
    assert CommissioningSwarm().run("life-safety-cx-gate", _load("life_safety_abort.yaml")).decision == "ABORT"

def test_plan_hold():
    assert CommissioningSwarm().run("pre-cx-gate", _load("plan_hold.yaml")).decision == "HOLD"

def test_om_hold():
    assert CommissioningSwarm().run("om-training-gate", _load("om_hold.yaml")).decision == "HOLD"

def test_cx_closeout_go():
    assert CommissioningSwarm().run("cx-closeout", _load("pre_cx_go.yaml")).decision == "GO"

def test_hold_abort():
    assert CommissioningSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "life-safety"}).decision == "ABORT"
