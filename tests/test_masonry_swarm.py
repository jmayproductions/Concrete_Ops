from __future__ import annotations

from pathlib import Path
import yaml
from modules.masonry_swarm.swarm import MasonrySwarm
from modules.masonry_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "masonry" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(MasonrySwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_masonry_go():
    assert MasonrySwarm().run("pre-masonry-gate", _load("pre_masonry_go.yaml")).decision == "GO"


def test_grout_lift_hold():
    assert MasonrySwarm().run("grout-lift-runbook", _load("grout_lift_hold.yaml")).decision == "HOLD"


def test_weeps_blocked_hold():
    assert MasonrySwarm().run("flashing-weep-qa", _load("weeps_blocked_hold.yaml")).decision == "HOLD"


def test_cold_weather_hold():
    assert MasonrySwarm().run("pre-masonry-gate", _load("cold_weather_hold.yaml")).decision == "HOLD"


def test_unstable_wall_abort():
    assert MasonrySwarm().run("daily-layup-runbook", _load("unstable_wall_abort.yaml")).decision == "ABORT"


def test_rebar_dirty_hold():
    assert MasonrySwarm().run("rebar-pregrout-gate", _load("rebar_dirty_hold.yaml")).decision == "HOLD"


def test_daily_layup_go():
    assert MasonrySwarm().run("daily-layup-runbook", _load("pre_masonry_go.yaml")).decision == "GO"


def test_closeout_go():
    assert MasonrySwarm().run("masonry-closeout", _load("pre_masonry_go.yaml")).decision == "GO"


def test_hold_abort():
    assert MasonrySwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "scaffold"}).decision == "ABORT"
