from __future__ import annotations

from pathlib import Path
import yaml
from modules.heavy_lift_swarm.swarm import HeavyLiftSwarm
from modules.heavy_lift_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "heavy-lift" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(HeavyLiftSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_lift_go():
    assert HeavyLiftSwarm().run("pre-lift-gate", _load("pre_lift_go.yaml")).decision == "GO"


def test_wind_abort():
    assert HeavyLiftSwarm().run("weather-wind-gate", _load("wind_abort.yaml")).decision == "ABORT"


def test_under_load_abort():
    assert HeavyLiftSwarm().run("exclusion-zone-gate", _load("under_load_abort.yaml")).decision == "ABORT"


def test_overload_abort():
    assert HeavyLiftSwarm().run("load-chart-gate", _load("overload_abort.yaml")).decision == "ABORT"


def test_power_line_abort():
    assert HeavyLiftSwarm().run("power-line-clearance", _load("power_line_abort.yaml")).decision == "ABORT"


def test_soft_ground_hold():
    assert HeavyLiftSwarm().run("ground-bearing-gate", _load("soft_ground_hold.yaml")).decision == "HOLD"


def test_critical_go():
    assert HeavyLiftSwarm().run("critical-lift-runbook", _load("pre_lift_go.yaml")).decision == "GO"


def test_closeout_go():
    assert HeavyLiftSwarm().run("post-lift-closeout", _load("pre_lift_go.yaml")).decision == "GO"


def test_hold_abort():
    assert HeavyLiftSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "wind"}).decision == "ABORT"
