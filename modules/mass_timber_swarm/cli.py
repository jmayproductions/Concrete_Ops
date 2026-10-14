"""CLI for mass timber sequencing swarm workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.mass_timber_swarm.swarm import TimberSwarm

app = typer.Typer(
    add_completion=False,
    help="Mass timber sequencing swarm — engineered wood erection workflows",
)


def _load_context(path: Optional[Path]) -> dict:
    if path is None:
        return {}
    text = path.read_text()
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(text) or {}
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise typer.BadParameter("Context file must contain a JSON/YAML object")
    return data


@app.command("list")
def list_workflows() -> None:
    """List named repeatable erection workflows."""
    for workflow_id in TimberSwarm().list_workflows():
        print(f"- {workflow_id}")


@app.command("run")
def run_workflow(
    workflow: str = typer.Argument(..., help="Workflow id, e.g. pre-erect-gate"),
    context_file: Optional[Path] = typer.Option(
        None, "--context", "-c", help="JSON/YAML erect context"
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
) -> None:
    """Run one swarm workflow and print the decision packet."""
    swarm = TimberSwarm()
    result = swarm.run(workflow, _load_context(context_file))
    if as_json:
        print(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        print(result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo_pre_erect() -> None:
    """Run a built-in GO pre-erect demo context."""
    context = {
        "erect_id": "DEMO-L4-ZONE-A",
        "level": "Level 4 Zone A",
        "pre_erect_go": True,
        "supply": {
            "shop_drawings_approved": True,
            "erection_drawings_approved": True,
            "sequence_published": True,
            "cnc_complete": True,
            "truck": {
                "expected_piece_marks": ["CLT-401", "GLT-12"],
                "onboard_piece_marks": ["CLT-401", "GLT-12"],
            },
        },
        "survey": {
            "within_tolerance": True,
            "podium_asbuilt": True,
            "embeds_verified": True,
            "grid_control": True,
        },
        "hybrid": {
            "podium_released": True,
            "steel_primed_or_na": True,
            "movement_details_ok": True,
        },
        "crane": {
            "chart_ok": True,
            "pick_points_verified": True,
            "exclusion_zone_set": True,
            "trailer_direct": True,
        },
        "moisture": {
            "mmp_approved": True,
            "protection_materials_staged": True,
            "moisture_content_pct": 12.0,
            "max_mc_pct": 16.0,
            "standing_water": False,
            "joints_sealed": True,
        },
        "bracing": {
            "plan_issued": True,
            "shear_wall_brace_plan": True,
            "braces_installed": True,
            "diaphragm_locked": True,
        },
        "connections": {"hardware_kits_matched": True, "incomplete_patterns": []},
        "panels": {
            "sequence": ["CLT-401", "CLT-402"],
            "seated": True,
            "force_fit": False,
            "field_cut_unapproved": False,
        },
        "glulam": {
            "camber_orientation_ok": True,
            "base_hardware_ready": True,
            "seats_ready": True,
        },
        "weather": {"wind_kph": 18, "active_precip": False},
        "crew": {
            "roles": [
                "erect_lead",
                "crane_operator",
                "rigger",
                "connector",
                "brace_crew",
                "qc_tech",
                "safety_watch",
            ],
            "headcount": 10,
            "briefing_complete": True,
            "fatigued_workers": [],
        },
        "assembly": {
            "fire_sequencing_ok": True,
            "mep_openings_coordinated": True,
            "acoustic_stack_ready": True,
        },
        "finish": {"exposed_architecture": True, "protection_plan": True, "padded_rigging": True},
        "qa": {"pre_hold_points_clear": True, "pick_hold_points_clear": True},
        "safety": {"violations": []},
    }
    result = TimberSwarm().run("pre-erect-gate", context)
    print(result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


if __name__ == "__main__":
    app()
