# modules/cli/launch_menu.py

from rich.console import Console
from rich.prompt import Prompt
from modules.pour_manager.pour_status import PourStatusManager

console = Console()

def launch_cli_menu(config):
    while True:
        console.print("\n[bold blue]🧱 ConcreteOps CLI Menu[/bold blue]")
        console.print("1. Run Pour Status Check")
        console.print("2. Exit")

        choice = Prompt.ask("Choose an option", choices=["1", "2"], default="2")

        if choice == "1":
            manager = PourStatusManager(project_id="DEV-PROJECT-001")
            status = manager.get_status()
            console.print(f"[cyan]Current Pour Status:[/cyan] {status}")
        elif choice == "2":
            console.print("[bold red]Exiting ConcreteOps CLI.[/bold red]")
            break
