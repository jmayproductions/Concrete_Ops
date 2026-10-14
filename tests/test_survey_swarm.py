from __future__ import annotations

from pathlib import Path
import yaml
from modules.survey_swarm.swarm import SurveySwarm
from modules.survey_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "survey" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(SurveySwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_survey_go():
    assert SurveySwarm().run("pre-survey-gate", _load("pre_survey_go.yaml")).decision == "GO"


def test_control_destroyed_abort():
    assert SurveySwarm().run("stakeout-runbook", _load("control_destroyed_abort.yaml")).decision == "ABORT"


def test_out_of_tolerance_hold():
    assert SurveySwarm().run("tolerance-accept-gate", _load("out_of_tolerance_hold.yaml")).decision == "HOLD"


def test_superseded_bim_hold():
    assert SurveySwarm().run("bim-layout-gate", _load("superseded_bim_hold.yaml")).decision == "HOLD"


def test_open_edge_abort():
    assert SurveySwarm().run("stakeout-runbook", _load("open_edge_abort.yaml")).decision == "ABORT"


def test_calibration_hold():
    assert SurveySwarm().run("pre-survey-gate", _load("calibration_hold.yaml")).decision == "HOLD"


def test_embed_go():
    assert SurveySwarm().run("embed-layout-gate", _load("pre_survey_go.yaml")).decision == "GO"


def test_closeout_go():
    assert SurveySwarm().run("survey-closeout", _load("pre_survey_go.yaml")).decision == "GO"


def test_hold_abort():
    assert SurveySwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "control"}).decision == "ABORT"
