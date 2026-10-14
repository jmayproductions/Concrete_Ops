from __future__ import annotations

from pathlib import Path
import yaml
from modules.precast_swarm.swarm import PrecastSwarm
from modules.precast_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "precast" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(PrecastSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_erect_go():
    assert PrecastSwarm().run("pre-erect-gate", _load("pre_erect_go.yaml")).decision == "GO"


def test_early_strength_hold():
    assert PrecastSwarm().run("fab-release-gate", _load("early_strength_hold.yaml")).decision == "HOLD"


def test_tag_mismatch_hold():
    assert PrecastSwarm().run("delivery-panel-gate", _load("tag_mismatch_hold.yaml")).decision == "HOLD"


def test_wind_lift_hold():
    assert PrecastSwarm().run("weather-lift-hold", _load("wind_lift_hold.yaml")).decision == "HOLD"


def test_unbraced_abort():
    assert PrecastSwarm().run("bracing-lock", _load("unbraced_abort.yaml")).decision == "ABORT"


def test_lift_day_go():
    assert PrecastSwarm().run("lift-day-runbook", _load("pre_erect_go.yaml")).decision == "GO"


def test_brace_release_go():
    assert PrecastSwarm().run("brace-release-gate", _load("brace_release_go.yaml")).decision == "GO"


def test_closeout_go():
    assert PrecastSwarm().run("level-closeout", _load("pre_erect_go.yaml")).decision == "GO"


def test_hold_abort():
    assert PrecastSwarm().run("hold-abort", {"erect_id": "X", "severity": "ABORT", "block_reason": "rigging failure"}).decision == "ABORT"
