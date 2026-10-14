from __future__ import annotations

from pathlib import Path
import yaml
from modules.closeout_swarm.swarm import CloseoutSwarm
from modules.closeout_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "closeout" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(CloseoutSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_closeout_go():
    assert CloseoutSwarm().run("pre-closeout-gate", _load("pre_closeout_go.yaml")).decision == "GO"


def test_open_critical_punch_hold():
    assert CloseoutSwarm().run("pre-closeout-gate", _load("open_critical_punch_hold.yaml")).decision == "HOLD"


def test_egress_blocked_abort():
    assert CloseoutSwarm().run("life-safety-gate", _load("egress_blocked_abort.yaml")).decision == "ABORT"


def test_ncr_open_hold():
    assert CloseoutSwarm().run("ncr-closeout-gate", _load("ncr_open_hold.yaml")).decision == "HOLD"


def test_turnover_missing_docs_hold():
    assert CloseoutSwarm().run("turnover-package-gate", _load("turnover_missing_docs_hold.yaml")).decision == "HOLD"


def test_tco_go():
    assert CloseoutSwarm().run("tco-readiness-gate", _load("tco_go.yaml")).decision == "GO"


def test_punch_walk_go():
    assert CloseoutSwarm().run("punchlist-walk", _load("pre_closeout_go.yaml")).decision == "GO"


def test_turnover_go():
    assert CloseoutSwarm().run("turnover-package-gate", _load("pre_closeout_go.yaml")).decision == "GO"


def test_hold_abort():
    assert CloseoutSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "blocked egress"}).decision == "ABORT"
