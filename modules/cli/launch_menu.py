# modules/cli/launch_menu.py

from rich.console import Console
from rich.prompt import Prompt

from modules.agent_swarm.swarm import CrewSwarm

console = Console()


def launch_cli_menu(config):
    while True:
        console.print("\n[bold blue]ConcreteOps CLI Menu[/bold blue]")
        console.print("1. Run crew swarm demo (pre-pour-gate)")
        console.print("2. List crew swarm workflows")
        console.print("3. Exit")

        choice = Prompt.ask("Choose an option", choices=["1", "2", "3"], default="3")

        if choice == "1":
            swarm = CrewSwarm()
            result = swarm.run(
                "pre-pour-gate",
                {
                    "pour_id": "DEV-PROJECT-001",
                    "area": "Dev Deck",
                    "volume_cy": 40,
                    "mix": {
                        "ticket_id": "DEV-T1",
                        "psi": 4000,
                        "w_c_ratio": 0.42,
                        "slump": 5.0,
                        "air_content": 5.5,
                    },
                    "weather": {"temp_f": 70, "wind_kph": 10, "rain_mm": 0},
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
                        "headcount": 6,
                        "briefing_complete": True,
                        "fatigued_workers": [],
                    },
                    "telemetry": {"slump": 5.0, "temperature": 70},
                    "site_conditions": {"wind_speed": 8, "evaporation_rate": 0.1},
                },
            )
            console.print(result.render())
        elif choice == "2":
            for workflow_id in CrewSwarm().list_workflows():
                console.print(f"- {workflow_id}")
        elif choice == "3":
            console.print("[bold red]Exiting ConcreteOps CLI.[/bold red]")
            break
