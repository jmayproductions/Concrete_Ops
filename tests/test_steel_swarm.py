from __future__ import annotations

from pathlib import Path

import yaml

from modules.steel_swarm.swarm import SteelSwarm
from modules.steel_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "steel" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_expected_workflows():
    assert set(SteelSwarm().list_workflows()) == set(WORKFLOW_IDS)
    assert len(WORKFLOW_IDS) == 12


def test_pre_erect_go():
    result = SteelSwarm().run("pre-erect-gate", _load("pre_erect_go.yaml"))
    assert result.decision == "GO"
    assert any(g.agent == "fab-mill" and g.status == "PASS" for g in result.gates)


def test_delivery_heat_hold():
    result = SteelSwarm().run("delivery-piece-gate", _load("delivery_heat_hold.yaml"))
    assert result.decision == "HOLD"


def test_level_erect_go():
    result = SteelSwarm().run("level-erect-runbook", _load("pre_erect_go.yaml"))
    assert result.decision == "GO"


def test_bolting_hold():
    result = SteelSwarm().run("bolting-qa", _load("bolting_torque_hold.yaml"))
    assert result.decision == "HOLD"


def test_welding_ndt_hold():
    result = SteelSwarm().run("welding-ndt-gate", _load("welding_ndt_hold.yaml"))
    assert result.decision == "HOLD"


def test_bracing_abort():
    result = SteelSwarm().run("bracing-stability-lock", _load("bracing_abort.yaml"))
    assert result.decision == "ABORT"


def test_decking_release_go():
    result = SteelSwarm().run("decking-release", _load("decking_release_go.yaml"))
    assert result.decision == "GO"


def test_level_closeout_go():
    result = SteelSwarm().run("level-closeout", _load("pre_erect_go.yaml"))
    assert result.decision == "GO"


def test_hold_abort():
    result = SteelSwarm().run("hold-abort", {"erect_id": "X", "severity": "ABORT", "block_reason": "fall protection"})
    assert result.decision == "ABORT"


def test_unknown_workflow():
    try:
        SteelSwarm().run("nope", {})
        assert False
    except ValueError as exc:
        assert "Unknown workflow" in str(exc)
