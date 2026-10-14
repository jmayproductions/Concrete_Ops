"""CLI for CoreProof lab swarm."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import typer, yaml
from rich import print
from modules.coreproof_swarm.swarm import CoreProofSwarm

app = typer.Typer(add_completion=False, help="CoreProof lab verification field swarm")

def _load(path: Optional[Path]) -> dict:
    if path is None: return {}
    text = path.read_text()
    data = yaml.safe_load(text) if path.suffix.lower() in {".yaml", ".yml"} else json.loads(text)
    if not isinstance(data, dict):
        raise typer.BadParameter("Context must be an object")
    return data

@app.command("list")
def list_workflows() -> None:
    for w in CoreProofSwarm().list_workflows():
        print(f"- {w}")

@app.command("run")
def run_workflow(workflow: str, context_file: Optional[Path] = typer.Option(None, "--context", "-c"), as_json: bool = typer.Option(False, "--json")) -> None:
    result = CoreProofSwarm().run(workflow, _load(context_file))
    print(json.dumps(result.to_dict(), indent=2, default=str) if as_json else result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)

@app.command("demo")
def demo() -> None:
    fixture = Path(__file__).resolve().parents[2] / "agents" / "coreproof" / "fixtures" / "pre_sample_go.yaml"
    result = CoreProofSwarm().run("pre-sample-gate", yaml.safe_load(fixture.read_text()))
    print(result.render())
    raise typer.Exit(0 if result.decision == "GO" else 2)

if __name__ == "__main__":
    app()
