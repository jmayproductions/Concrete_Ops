"""CLI for structural steel erection swarm workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print

from modules.steel_swarm.swarm import SteelSwarm

app = typer.Typer(add_completion=False, help="Structural steel erection swarm")


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
    for workflow_id in SteelSwarm().list_workflows():
        print(f"- {workflow_id}")


@app.command("run")
def run_workflow(
    workflow: str = typer.Argument(...),
    context_file: Optional[Path] = typer.Option(None, "--context", "-c"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    result = SteelSwarm().run(workflow, _load_context(context_file))
    if as_json:
        print(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        print(result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


@app.command("demo")
def demo_pre_erect() -> None:
    from pathlib import Path
    import yaml

    fixture = Path(__file__).resolve().parents[2] / "agents" / "steel" / "fixtures" / "pre_erect_go.yaml"
    result = SteelSwarm().run("pre-erect-gate", yaml.safe_load(fixture.read_text()))
    print(result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)


if __name__ == "__main__":
    app()
