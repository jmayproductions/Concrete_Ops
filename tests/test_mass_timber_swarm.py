from __future__ import annotations

from pathlib import Path

import yaml

from modules.mass_timber_swarm.swarm import TimberSwarm
from modules.mass_timber_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "mass-timber" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_expected_workflows():
    assert set(TimberSwarm().list_workflows()) == set(WORKFLOW_IDS)
    assert len(WORKFLOW_IDS) == 12


def test_pre_erect_go_fixture():
    result = TimberSwarm().run("pre-erect-gate", _load("pre_erect_go.yaml"))
    assert result.decision == "GO"
    assert result.workflow == "pre-erect-gate"
    assert any(g.agent == "supply-chain" and g.status == "PASS" for g in result.gates)
    assert any(g.agent == "moisture-protect" and g.status == "PASS" for g in result.gates)
    assert "DECISION: GO" in result.render()


def test_weather_wind_hold():
    result = TimberSwarm().run("pre-erect-gate", _load("weather_wind_hold.yaml"))
    assert result.decision == "HOLD"
    weather = next(g for g in result.gates if g.agent == "weather-gate")
    assert weather.status == "HOLD"


def test_delivery_jit_piece_mark_hold():
    result = TimberSwarm().run("delivery-jit-gate", _load("delivery_jit_hold.yaml"))
    assert result.decision == "HOLD"
    supply = next(g for g in result.gates if g.agent == "supply-chain")
    assert supply.status == "HOLD"
    assert "piece marks" in supply.detail.lower()


def test_level_erect_runbook_go():
    result = TimberSwarm().run("level-erect-runbook", _load("level_erect_go.yaml"))
    assert result.decision == "GO"
    assert any(g.agent == "temp-bracing" for g in result.gates)


def test_panel_placement_go():
    result = TimberSwarm().run("panel-placement", _load("pre_erect_go.yaml"))
    assert result.decision == "GO"


def test_glulam_frame_erect_go():
    result = TimberSwarm().run("glulam-frame-erect", _load("pre_erect_go.yaml"))
    assert result.decision == "GO"


def test_bracing_diaphragm_lock_go():
    result = TimberSwarm().run("bracing-diaphragm-lock", _load("pre_erect_go.yaml"))
    assert result.decision == "GO"


def test_bracing_unstable_abort():
    result = TimberSwarm().run("bracing-diaphragm-lock", _load("bracing_abort.yaml"))
    assert result.decision == "ABORT"
    safety = next(g for g in result.gates if g.agent == "safety-failsafe")
    assert safety.status == "FAIL"


def test_moisture_daily_hold():
    result = TimberSwarm().run("moisture-daily-check", _load("moisture_daily_hold.yaml"))
    assert result.decision == "HOLD"
    moisture = next(g for g in result.gates if g.agent == "moisture-protect")
    assert moisture.status == "HOLD"
    assert "MC" in moisture.detail


def test_connection_incomplete_hold():
    result = TimberSwarm().run("connection-qa", _load("connection_incomplete_hold.yaml"))
    assert result.decision == "HOLD"
    conn = next(g for g in result.gates if g.agent == "connections")
    assert conn.status == "HOLD"


def test_hybrid_interface_go():
    result = TimberSwarm().run("hybrid-interface-gate", _load("hybrid_interface_go.yaml"))
    assert result.decision == "GO"


def test_topping_release_go():
    result = TimberSwarm().run("topping-release", _load("topping_release_go.yaml"))
    assert result.decision == "GO"


def test_level_closeout_go():
    result = TimberSwarm().run("level-closeout", _load("pre_erect_go.yaml"))
    assert result.decision == "GO"


def test_crane_overload_abort_on_panel_placement():
    result = TimberSwarm().run("panel-placement", _load("crane_overload_abort.yaml"))
    assert result.decision == "ABORT"
    safety = next(g for g in result.gates if g.agent == "safety-failsafe")
    assert safety.status == "FAIL"


def test_hold_abort_escalation():
    result = TimberSwarm().run(
        "hold-abort",
        {"erect_id": "X", "severity": "ABORT", "block_reason": "unstable bay"},
    )
    assert result.decision == "ABORT"


def test_unknown_workflow_raises():
    try:
        TimberSwarm().run("not-a-workflow", {})
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "Unknown workflow" in str(exc)


def test_force_fit_panel_hold():
    ctx = _load("pre_erect_go.yaml")
    ctx["panels"]["force_fit"] = True
    result = TimberSwarm().run("panel-placement", ctx)
    assert result.decision == "HOLD"
    panels = next(g for g in result.gates if g.agent == "panel-erect")
    assert panels.status == "HOLD"
