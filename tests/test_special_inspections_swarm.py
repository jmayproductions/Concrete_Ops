from __future__ import annotations

from pathlib import Path
import yaml
from modules.special_inspections_swarm.swarm import SpecialInspectionsSwarm
from modules.special_inspections_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "special-inspections" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(SpecialInspectionsSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_si_go():
    assert SpecialInspectionsSwarm().run("pre-si-program-gate", _load("pre_si_go.yaml")).decision == "GO"


def test_cover_without_si_abort():
    assert SpecialInspectionsSwarm().run("cover-before-si-gate", _load("cover_without_si_abort.yaml")).decision == "ABORT"


def test_unapproved_agency_abort():
    assert SpecialInspectionsSwarm().run("pre-si-program-gate", _load("unapproved_agency_abort.yaml")).decision == "ABORT"


def test_pour_no_inspector_hold():
    assert SpecialInspectionsSwarm().run("concrete-pour-si-gate", _load("pour_no_inspector_hold.yaml")).decision == "HOLD"


def test_ndt_open_hold():
    assert SpecialInspectionsSwarm().run("ndt-release-gate", _load("ndt_open_hold.yaml")).decision == "HOLD"


def test_sossi_missing_hold():
    assert SpecialInspectionsSwarm().run("pre-si-program-gate", _load("sossi_missing_hold.yaml")).decision == "HOLD"


def test_concrete_go():
    assert SpecialInspectionsSwarm().run("concrete-pour-si-gate", _load("pre_si_go.yaml")).decision == "GO"


def test_final_report_go():
    assert SpecialInspectionsSwarm().run("si-final-report", _load("pre_si_go.yaml")).decision == "GO"


def test_hold_abort():
    assert SpecialInspectionsSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "cover"}).decision == "ABORT"
