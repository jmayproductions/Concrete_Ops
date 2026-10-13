"""CLI for ConcreteOps crew swarm workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.agent_swarm.swarm import CrewSwarm

app = typer.Typer(add_completion=False, help="ConcreteOps crew swarm — repeatable pour workflows")


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
    """List named repeatable workflows."""
    for workflow_id in CrewSwarm().list_workflows():
        print(f"- {workflow_id}")


@app.command("run")
def run_workflow(
    workflow: str = typer.Argument(..., help="Workflow id, e.g. pre-pour-gate"),
    context_file: Optional[Path] = typer.Option(
        None, "--context", "-c", help="JSON/YAML pour context"
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
) -> None:
    """Run one swarm workflow and print the decision packet."""
    swarm = CrewSwarm()
    result = swarm.run(workflow, _load_context(context_file))
    if as_json:
        print(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        print(result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo_pre_pour() -> None:
    """Run a built-in GO pre-pour demo context."""
    context = {
        "pour_id": "DEMO-L3-DECK-A",
        "area": "Level 3 Deck A",
        "volume_cy": 120,
        "mix": {
            "ticket_id": "T-1001",
            "psi": 4000,
            "w_c_ratio": 0.42,
            "slump": 5.0,
            "air_content": 5.5,
        },
        "weather": {"temp_f": 68, "wind_kph": 12, "rain_mm": 0},
        "readiness": {
            "forms_ready": True,
            "rebar_ready": True,
            "cylinders_ready": True,
        },
        "crew": {
            "roles": [
                "pour_lead",
                "pump_operator",
                "vibrator",
                "finisher",
                "qc_tech",
                "safety_watch",
            ],
            "headcount": 8,
            "briefing_complete": True,
            "fatigued_workers": [],
        },
        "telemetry": {"slump": 5.0, "temperature": 72},
        "site_conditions": {"wind_speed": 8, "evaporation_rate": 0.1},
    }
    result = CrewSwarm().run("pre-pour-gate", context)
    print(result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


if __name__ == "__main__":
    app()
