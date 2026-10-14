from __future__ import annotations

from pathlib import Path
import yaml
from modules.mep_swarm.swarm import MepSwarm
from modules.mep_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "mep" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(MepSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_mep_go():
    assert MepSwarm().run("pre-mep-gate", _load("pre_mep_go.yaml")).decision == "GO"


def test_clash_hold():
    assert MepSwarm().run("clash-sleeve-gate", _load("clash_hold.yaml")).decision == "HOLD"


def test_firestop_hold():
    assert MepSwarm().run("firestop-precover-gate", _load("firestop_hold.yaml")).decision == "HOLD"


def test_cover_without_firestop_abort():
    assert MepSwarm().run("inwall-cover-release", _load("cover_without_firestop_abort.yaml")).decision == "ABORT"


def test_pressure_fail_hold():
    r = MepSwarm().run("pressure-test-gate", _load("pressure_test_fail.yaml"))
    assert r.decision == "HOLD"


def test_hvac_go():
    assert MepSwarm().run("hvac-rough-runbook", _load("pre_mep_go.yaml")).decision == "GO"


def test_inwall_cover_go():
    assert MepSwarm().run("inwall-cover-release", _load("pre_mep_go.yaml")).decision == "GO"


def test_closeout_go():
    assert MepSwarm().run("mep-closeout", _load("pre_mep_go.yaml")).decision == "GO"


def test_hold_abort():
    assert MepSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "LOTO"}).decision == "ABORT"
