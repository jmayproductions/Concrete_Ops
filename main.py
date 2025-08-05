# main.py

"""
ConcreteOps™ Launcher — Dev CLI
Launches core modules, toggles dev modes, and routes to field logic.
"""

import typer
from rich import print
from shared.config_loader import load_config
from modules.cli.launch_menu import launch_cli_menu

app = typer.Typer()
config = load_config()

@app.command()
def start(mode: str = typer.Option("dev", help="Mode: dev | sim | field | prod")):
    print(f"[bold cyan]🚧 ConcreteOps™[/bold cyan] starting in [bold yellow]{mode.upper()}[/bold yellow] mode...")

    # Store mode globally if needed
    config['global']['mode'] = mode.lower()

    # CLI Mode
    launch_cli_menu(config)

@app.command()
def version():
    print("[green]ConcreteOps v1.0 — StructureWave Certified.[/green]")

if __name__ == "__main__":
    app()
