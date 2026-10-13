from __future__ import annotations

from pathlib import Path

import yaml

from modules.agent_swarm.swarm import CrewSwarm
from modules.agent_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "concrete-crew" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_expected_workflows():
    assert set(CrewSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_pour_go_fixture():
    result = CrewSwarm().run("pre-pour-gate", _load("pre_pour_go.yaml"))
    assert result.decision == "GO"
    assert result.workflow == "pre-pour-gate"
    assert any(g.agent == "materials-mix" and g.status == "PASS" for g in result.gates)
    assert "DECISION: GO" in result.render()


def test_pre_pour_weather_hold():
    result = CrewSwarm().run("pre-pour-gate", _load("pre_pour_weather_hold.yaml"))
    assert result.decision == "HOLD"
    weather = next(g for g in result.gates if g.agent == "weather-gate")
    assert weather.status == "HOLD"


def test_failsafe_abort_on_pour_day():
    result = CrewSwarm().run("pour-day-runbook", _load("failsafe_abort.yaml"))
    assert result.decision == "ABORT"
    safety = next(g for g in result.gates if g.agent == "safety-failsafe")
    assert safety.status == "FAIL"


def test_crew_briefing_incomplete():
    ctx = _load("pre_pour_go.yaml")
    ctx["crew"]["briefing_items"] = ["pour_identity"]
    result = CrewSwarm().run("crew-briefing", ctx)
    assert result.decision == "HOLD"


def test_crew_briefing_complete():
    result = CrewSwarm().run("crew-briefing", _load("pre_pour_go.yaml"))
    assert result.decision == "GO"


def test_post_pour_closeout_go():
    result = CrewSwarm().run("post-pour-closeout", _load("pre_pour_go.yaml"))
    assert result.decision == "GO"


def test_mid_pour_monitor_go():
    result = CrewSwarm().run("mid-pour-monitor", _load("pre_pour_go.yaml"))
    assert result.decision == "GO"


def test_hold_abort_escalation():
    result = CrewSwarm().run(
        "hold-abort",
        {"pour_id": "X", "severity": "ABORT", "block_reason": "form blowout"},
    )
    assert result.decision == "ABORT"


def test_unknown_workflow_raises():
    try:
        CrewSwarm().run("not-a-workflow", {})
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "Unknown workflow" in str(exc)


def test_pt_pre_stress_go():
    result = CrewSwarm().run("pt-pre-stress-gate", _load("pt_pre_stress_go.yaml"))
    assert result.decision == "GO"
    assert any(g.agent == "pt-stress" and g.status == "PASS" for g in result.gates)


def test_pt_stress_sequence_go():
    result = CrewSwarm().run("pt-stress-sequence", _load("pt_pre_stress_go.yaml"))
    assert result.decision == "GO"


def test_pt_elongation_hold():
    result = CrewSwarm().run("pt-stress-sequence", _load("pt_elongation_hold.yaml"))
    assert result.decision == "HOLD"
    pt = next(g for g in result.gates if g.agent == "pt-stress")
    assert pt.status == "HOLD"
    assert "elongation" in pt.detail.lower() or "inspected" in pt.detail.lower()


def test_tilt_cast_go():
    result = CrewSwarm().run("tilt-up-cast-gate", _load("tilt_cast_go.yaml"))
    assert result.decision == "GO"


def test_tilt_cast_missing_embeds_fail_hold():
    ctx = _load("tilt_cast_go.yaml")
    ctx["tilt"]["panels"][0]["embeds_complete"] = False
    result = CrewSwarm().run("tilt-up-cast-gate", ctx)
    assert result.decision == "HOLD"
    tilt = next(g for g in result.gates if g.agent == "tilt-up")
    assert tilt.status == "FAIL"


def test_tilt_lift_wind_hold():
    result = CrewSwarm().run("tilt-up-lift-day", _load("tilt_lift_wind_hold.yaml"))
    assert result.decision == "HOLD"
    assert any(
        g.agent in ("tilt-up", "weather-gate") and g.status == "HOLD" for g in result.gates
    )


def test_tilt_brace_release_go():
    result = CrewSwarm().run("tilt-up-brace-release", _load("tilt_brace_release_go.yaml"))
    assert result.decision == "GO"


def test_tilt_brace_release_instability_abort():
    ctx = _load("tilt_brace_release_go.yaml")
    ctx["tilt"]["panels"][0]["instability"] = True
    result = CrewSwarm().run("tilt-up-brace-release", ctx)
    assert result.decision == "ABORT"


def test_sog_pre_pour_go():
    result = CrewSwarm().run("sog-pre-pour-gate", _load("sog_pre_pour_go.yaml"))
    assert result.decision == "GO"


def test_sog_finish_hold():
    result = CrewSwarm().run("sog-finish-fffl", _load("sog_finish_hold.yaml"))
    assert result.decision == "HOLD"
    sog = next(g for g in result.gates if g.agent == "sog")
    assert sog.status == "HOLD"


def test_shotcrete_placement_go():
    result = CrewSwarm().run("shotcrete-placement", _load("shotcrete_go.yaml"))
    assert result.decision == "GO"


def test_shotcrete_rebound_hold():
    result = CrewSwarm().run("shotcrete-placement", _load("shotcrete_rebound_hold.yaml"))
    assert result.decision == "HOLD"


def test_cip_wall_pour_go():
    result = CrewSwarm().run("cip-wall-pour", _load("cip_wall_go.yaml"))
    assert result.decision == "GO"


def test_cip_wall_pressure_abort():
    result = CrewSwarm().run("cip-wall-pour", _load("cip_wall_pressure_abort.yaml"))
    assert result.decision == "ABORT"
