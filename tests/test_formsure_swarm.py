from __future__ import annotations

from pathlib import Path
import yaml
from modules.formsure_swarm.swarm import FormSureSwarm
from modules.formsure_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "formsure" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(FormSureSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_pour_go():
    assert FormSureSwarm().run("pre-pour-form-gate", _load("pre_pour_go.yaml")).decision == "GO"


def test_loose_ties_abort():
    assert FormSureSwarm().run("tie-brace-gate", _load("loose_ties_abort.yaml")).decision == "ABORT"


def test_drop_height_abort():
    assert FormSureSwarm().run("pour-drop-gate", _load("drop_height_abort.yaml")).decision == "ABORT"


def test_overrate_abort():
    assert FormSureSwarm().run("form-pressure-gate", _load("overrate_abort.yaml")).decision == "ABORT"


def test_early_strip_abort():
    assert FormSureSwarm().run("strip-readiness-gate", _load("early_strip_abort.yaml")).decision == "ABORT"


def test_soft_shore_hold():
    assert FormSureSwarm().run("shore-stability-gate", _load("soft_shore_hold.yaml")).decision == "HOLD"


def test_release_hold():
    assert FormSureSwarm().run("release-agent-check", _load("release_hold.yaml")).decision == "HOLD"


def test_closeout_go():
    assert FormSureSwarm().run("post-strip-closeout", _load("pre_pour_go.yaml")).decision == "GO"


def test_hold_abort():
    assert FormSureSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "blowout"}).decision == "ABORT"
