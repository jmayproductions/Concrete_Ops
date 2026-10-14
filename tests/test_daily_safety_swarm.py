from __future__ import annotations

from pathlib import Path
import yaml
from modules.daily_safety_swarm.swarm import DailySafetySwarm
from modules.daily_safety_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "daily-safety" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(DailySafetySwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_shift_go():
    assert DailySafetySwarm().run("pre-shift-safety-gate", _load("pre_shift_go.yaml")).decision == "GO"


def test_hot_work_no_permit_abort():
    assert DailySafetySwarm().run("hot-work-permit-gate", _load("hot_work_no_permit_abort.yaml")).decision == "ABORT"


def test_cse_gas_abort():
    assert DailySafetySwarm().run("confined-space-entry", _load("cse_gas_abort.yaml")).decision == "ABORT"


def test_fall_unprotected_abort():
    assert DailySafetySwarm().run("fall-protection-gate", _load("fall_unprotected_abort.yaml")).decision == "ABORT"


def test_incident_stop_abort():
    assert DailySafetySwarm().run("incident-abort", _load("incident_stop_abort.yaml")).decision == "ABORT"


def test_briefing_hold():
    assert DailySafetySwarm().run("pre-shift-safety-gate", _load("briefing_hold.yaml")).decision == "HOLD"


def test_hot_work_go():
    assert DailySafetySwarm().run("hot-work-permit-gate", _load("pre_shift_go.yaml")).decision == "GO"


def test_crane_go():
    assert DailySafetySwarm().run("crane-exclusion-gate", _load("pre_shift_go.yaml")).decision == "GO"


def test_hold_abort():
    assert DailySafetySwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "stop-work"}).decision == "ABORT"
