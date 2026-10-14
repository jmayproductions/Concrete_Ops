from __future__ import annotations
from pathlib import Path
import yaml
from modules.life_safety_swarm.swarm import LifeSafetySwarm
from modules.life_safety_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "life-safety" / "fixtures"

def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())

def test_lists_workflows():
    assert set(LifeSafetySwarm().list_workflows()) == set(WORKFLOW_IDS)

def test_pre_ls_go():
    assert LifeSafetySwarm().run("pre-ls-gate", _load("pre_ls_go.yaml")).decision == "GO"

def test_tco_go():
    assert LifeSafetySwarm().run("tco-readiness", _load("pre_ls_go.yaml")).decision == "GO"

def test_egress_blocked_abort():
    assert LifeSafetySwarm().run("egress-path-gate", _load("egress_blocked_abort.yaml")).decision == "ABORT"

def test_fire_door_abort():
    assert LifeSafetySwarm().run("fire-door-gate", _load("fire_door_abort.yaml")).decision == "ABORT"

def test_sprinkler_hydro_abort():
    assert LifeSafetySwarm().run("sprinkler-hydro-gate", _load("sprinkler_hydro_abort.yaml")).decision == "ABORT"

def test_alarm_dba_abort():
    assert LifeSafetySwarm().run("fire-alarm-gate", _load("alarm_dba_abort.yaml")).decision == "ABORT"

def test_egress_light_abort():
    assert LifeSafetySwarm().run("egress-lighting-gate", _load("egress_light_abort.yaml")).decision == "ABORT"

def test_hardware_hold():
    assert LifeSafetySwarm().run("door-hardware-gate", _load("hardware_hold.yaml")).decision == "HOLD"

def test_punch_reopen_hold():
    assert LifeSafetySwarm().run("punch-walk-gate", _load("punch_reopen_hold.yaml")).decision == "HOLD"

def test_hold_abort():
    assert LifeSafetySwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "egress"}).decision == "ABORT"
