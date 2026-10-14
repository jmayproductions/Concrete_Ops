from __future__ import annotations

from pathlib import Path
import yaml
from modules.interiors_swarm.swarm import InteriorsSwarm
from modules.interiors_swarm.workflows import WORKFLOW_IDS

FIXTURES = Path(__file__).resolve().parents[1] / "agents" / "interiors" / "fixtures"


def _load(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text())


def test_lists_workflows():
    assert set(InteriorsSwarm().list_workflows()) == set(WORKFLOW_IDS)


def test_pre_interiors_go():
    assert InteriorsSwarm().run("pre-interiors-gate", _load("pre_interiors_go.yaml")).decision == "GO"


def test_no_cover_release_hold():
    assert InteriorsSwarm().run("inwall-cover-release", _load("no_cover_release_hold.yaml")).decision == "HOLD"


def test_shaft_compromised_abort():
    assert InteriorsSwarm().run("shaftwall-gate", _load("shaft_compromised_abort.yaml")).decision == "ABORT"


def test_stc_flanking_hold():
    assert InteriorsSwarm().run("acoustics-stc-gate", _load("stc_flanking_hold.yaml")).decision == "HOLD"


def test_wet_board_hold():
    assert InteriorsSwarm().run("pre-interiors-gate", _load("wet_board_hold.yaml")).decision == "HOLD"


def test_scaffold_abort():
    assert InteriorsSwarm().run("board-hang-runbook", _load("scaffold_abort.yaml")).decision == "ABORT"


def test_board_hang_go():
    assert InteriorsSwarm().run("board-hang-runbook", _load("pre_interiors_go.yaml")).decision == "GO"


def test_closeout_go():
    assert InteriorsSwarm().run("interiors-closeout", _load("pre_interiors_go.yaml")).decision == "GO"


def test_hold_abort():
    assert InteriorsSwarm().run("hold-abort", {"zone_id": "X", "severity": "ABORT", "block_reason": "egress"}).decision == "ABORT"
