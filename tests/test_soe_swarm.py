from __future__ import annotations

from pathlib import Path
import yaml
from modules.soe_swarm.swarm import SoeSwarm
from modules.soe_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "soe" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(SoeSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_soe_go():
    assert SoeSwarm().run("pre-soe-gate", _load("pre_soe_go.yaml")).decision == "GO"


def test_over_excavate_abort():
    assert SoeSwarm().run("excavation-stage-gate", _load("over_excavate_abort.yaml")).decision == "ABORT"


def test_monitoring_alarm_abort():
    assert SoeSwarm().run("monitoring-alarm-gate", _load("monitoring_alarm_abort.yaml")).decision == "ABORT"


def test_tieback_fail_hold():
    assert SoeSwarm().run("tieback-test-gate", _load("tieback_fail_hold.yaml")).decision == "HOLD"


def test_premature_release_abort():
    assert SoeSwarm().run("brace-release-gate", _load("premature_release_abort.yaml")).decision == "ABORT"


def test_design_missing_hold():
    assert SoeSwarm().run("pre-soe-gate", _load("design_missing_hold.yaml")).decision == "HOLD"


def test_stage_go():
    assert SoeSwarm().run("excavation-stage-gate", _load("pre_soe_go.yaml")).decision == "GO"


def test_closeout_go():
    assert SoeSwarm().run("soe-closeout", _load("pre_soe_go.yaml")).decision == "GO"


def test_hold_abort():
    assert SoeSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "collapse"}).decision == "ABORT"
