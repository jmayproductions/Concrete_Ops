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
