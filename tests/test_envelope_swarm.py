from __future__ import annotations

from pathlib import Path
import yaml
from modules.envelope_swarm.swarm import EnvelopeSwarm
from modules.envelope_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "envelope" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(EnvelopeSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_envelope_go():
    assert EnvelopeSwarm().run("pre-envelope-gate", _load("pre_envelope_go.yaml")).decision == "GO"


def test_below_grade_protection_hold():
    r = EnvelopeSwarm().run("below-grade-wp-runbook", _load("below_grade_protection_hold.yaml"))
    assert r.decision == "HOLD"


def test_roofing_go():
    assert EnvelopeSwarm().run("roofing-membrane-runbook", _load("pre_envelope_go.yaml")).decision == "GO"


def test_water_test_fail_hold():
    r = EnvelopeSwarm().run("water-test-gate", _load("water_test_fail.yaml"))
    assert r.decision == "HOLD"
    assert next(g for g in r.gates if g.agent == "water-test").status == "FAIL"


def test_backfill_abort():
    assert EnvelopeSwarm().run("below-grade-wp-runbook", _load("backfill_abort.yaml")).decision == "ABORT"


def test_cold_weather_hold():
    assert EnvelopeSwarm().run("pre-envelope-gate", _load("cold_weather_hold.yaml")).decision == "HOLD"


def test_curtain_wall_go():
    assert EnvelopeSwarm().run("curtain-wall-install-gate", _load("pre_envelope_go.yaml")).decision == "GO"


def test_closeout_go():
    assert EnvelopeSwarm().run("envelope-closeout", _load("pre_envelope_go.yaml")).decision == "GO"


def test_hold_abort():
    assert EnvelopeSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "open edge"}).decision == "ABORT"
