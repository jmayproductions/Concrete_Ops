from __future__ import annotations
from pathlib import Path
import yaml
from modules.roofing_swarm.swarm import RoofingSwarm
from modules.roofing_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "roofing" / "fixtures"

def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())

def test_lists_workflows():
    assert set(RoofingSwarm().list_workflows()) == set(WORKFLOW_IDS)

def test_pre_roof_go():
    assert RoofingSwarm().run("pre-roof-gate", _load("pre_roof_go.yaml")).decision == "GO"

def test_skipper_nails_abort():
    assert RoofingSwarm().run("fastener-gate", _load("skipper_nails_abort.yaml")).decision == "ABORT"

def test_missing_flashing_abort():
    assert RoofingSwarm().run("flashing-gate", _load("missing_flashing_abort.yaml")).decision == "ABORT"

def test_underlay_hold():
    assert RoofingSwarm().run("underlayment-gate", _load("underlay_bridge_hold.yaml")).decision == "HOLD"

def test_high_wind_staples_abort():
    assert RoofingSwarm().run("high-wind-gate", _load("high_wind_staples_abort.yaml")).decision == "ABORT"

def test_membrane_hold():
    assert RoofingSwarm().run("membrane-flat-gate", _load("membrane_seam_hold.yaml")).decision == "HOLD"

def test_no_starter_abort():
    assert RoofingSwarm().run("shingle-course-gate", _load("no_starter_abort.yaml")).decision == "ABORT"

def test_final_go():
    assert RoofingSwarm().run("final-inspection", _load("pre_roof_go.yaml")).decision == "GO"

def test_hold_abort():
    assert RoofingSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "leak"}).decision == "ABORT"
