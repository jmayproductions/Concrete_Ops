from __future__ import annotations
from pathlib import Path
import yaml
from modules.coreproof_swarm.swarm import CoreProofSwarm
from modules.coreproof_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "coreproof" / "fixtures"

def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())

def test_lists_workflows():
    assert set(CoreProofSwarm().list_workflows()) == set(WORKFLOW_IDS)

def test_pre_sample_go():
    assert CoreProofSwarm().run("pre-sample-gate", _load("pre_sample_go.yaml")).decision == "GO"

def test_low_strength_abort():
    assert CoreProofSwarm().run("low-strength-abort", _load("low_strength_abort.yaml")).decision == "ABORT"

def test_core_reject_abort():
    assert CoreProofSwarm().run("core-test-gate", _load("core_reject_abort.yaml")).decision == "ABORT"

def test_mishandle_hold():
    assert CoreProofSwarm().run("transport-lab-gate", _load("mishandle_hold.yaml")).decision == "HOLD"

def test_break_window_hold():
    assert CoreProofSwarm().run("break-schedule-gate", _load("break_window_hold.yaml")).decision == "HOLD"

def test_field_lab_hold():
    assert CoreProofSwarm().run("field-vs-lab-gate", _load("field_lab_deviation_hold.yaml")).decision == "HOLD"

def test_freeze_abort():
    assert CoreProofSwarm().run("pre-sample-gate", _load("freeze_abort.yaml")).decision == "ABORT"

def test_closeout_go():
    assert CoreProofSwarm().run("lab-closeout", _load("pre_sample_go.yaml")).decision == "GO"

def test_hold_abort():
    assert CoreProofSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "reject"}).decision == "ABORT"
