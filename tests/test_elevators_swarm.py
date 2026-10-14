from __future__ import annotations

from pathlib import Path
import yaml
from modules.elevators_swarm.swarm import ElevatorsSwarm
from modules.elevators_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "elevators" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(ElevatorsSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_elevator_go():
    assert ElevatorsSwarm().run("pre-elevator-gate", _load("pre_elevator_go.yaml")).decision == "GO"


def test_rails_out_hold():
    assert ElevatorsSwarm().run("rail-install-runbook", _load("rails_out_hold.yaml")).decision == "HOLD"


def test_open_hoistway_abort():
    assert ElevatorsSwarm().run("rail-install-runbook", _load("open_hoistway_abort.yaml")).decision == "ABORT"


def test_safety_bypass_abort():
    assert ElevatorsSwarm().run("temporary-run-gate", _load("safety_bypass_abort.yaml")).decision == "ABORT"


def test_ahj_punch_hold():
    assert ElevatorsSwarm().run("ahj-inspection-gate", _load("ahj_punch_hold.yaml")).decision == "HOLD"


def test_pit_not_ready_hold():
    assert ElevatorsSwarm().run("pre-elevator-gate", _load("pit_not_ready_hold.yaml")).decision == "HOLD"


def test_turnover_go():
    assert ElevatorsSwarm().run("elevator-turnover", _load("pre_elevator_go.yaml")).decision == "GO"


def test_safety_devices_go():
    assert ElevatorsSwarm().run("safety-devices-gate", _load("pre_elevator_go.yaml")).decision == "GO"


def test_hold_abort():
    assert ElevatorsSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "open hoistway"}).decision == "ABORT"
