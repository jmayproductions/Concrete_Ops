from __future__ import annotations

from pathlib import Path
import yaml
from modules.deep_foundations_swarm.swarm import DeepFoundationsSwarm
from modules.deep_foundations_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "deep-foundations" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(DeepFoundationsSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_foundation_go():
    assert DeepFoundationsSwarm().run("pre-foundation-gate", _load("pre_foundation_go.yaml")).decision == "GO"


def test_sediment_hold():
    assert DeepFoundationsSwarm().run("tip-elevation-gate", _load("sediment_hold.yaml")).decision == "HOLD"


def test_tremie_interrupt_hold():
    assert DeepFoundationsSwarm().run("tremie-pour-runbook", _load("tremie_interrupt_hold.yaml")).decision == "HOLD"


def test_open_hole_abort():
    assert DeepFoundationsSwarm().run("drilled-shaft-runbook", _load("open_hole_abort.yaml")).decision == "ABORT"


def test_driven_refusal_hold():
    assert DeepFoundationsSwarm().run("driven-pile-runbook", _load("driven_refusal_hold.yaml")).decision == "HOLD"


def test_integrity_anomaly_hold():
    assert DeepFoundationsSwarm().run("capacity-accept-gate", _load("integrity_anomaly_hold.yaml")).decision == "HOLD"


def test_tremie_go():
    assert DeepFoundationsSwarm().run("tremie-pour-runbook", _load("pre_foundation_go.yaml")).decision == "GO"


def test_closeout_go():
    assert DeepFoundationsSwarm().run("foundations-closeout", _load("pre_foundation_go.yaml")).decision == "GO"


def test_hold_abort():
    assert DeepFoundationsSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "open hole"}).decision == "ABORT"
