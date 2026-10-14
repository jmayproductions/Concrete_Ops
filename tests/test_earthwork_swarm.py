from __future__ import annotations

from pathlib import Path
import yaml
from modules.earthwork_swarm.swarm import EarthworkSwarm
from modules.earthwork_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "earthwork" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(EarthworkSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_earthwork_go():
    assert EarthworkSwarm().run("pre-earthwork-gate", _load("pre_earthwork_go.yaml")).decision == "GO"


def test_density_fail_hold():
    assert EarthworkSwarm().run("compaction-lift-runbook", _load("density_fail_hold.yaml")).decision == "HOLD"


def test_no_locate_abort():
    assert EarthworkSwarm().run("utilities-locate-gate", _load("no_locate_abort.yaml")).decision == "ABORT"


def test_pumping_subgrade_hold():
    assert EarthworkSwarm().run("subgrade-accept-gate", _load("pumping_subgrade_hold.yaml")).decision == "HOLD"


def test_unprotected_trench_abort():
    assert EarthworkSwarm().run("excavation-runbook", _load("unprotected_trench_abort.yaml")).decision == "ABORT"


def test_bmps_missing_hold():
    assert EarthworkSwarm().run("pre-earthwork-gate", _load("bmps_missing_hold.yaml")).decision == "HOLD"


def test_compaction_go():
    assert EarthworkSwarm().run("compaction-lift-runbook", _load("pre_earthwork_go.yaml")).decision == "GO"


def test_paving_prep_go():
    assert EarthworkSwarm().run("paving-prep-gate", _load("pre_earthwork_go.yaml")).decision == "GO"


def test_hold_abort():
    assert EarthworkSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "utility strike"}).decision == "ABORT"
