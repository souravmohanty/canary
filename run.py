# load_dotenv MUST run before any agent imports so Anthropic() picks up the key
from dotenv import load_dotenv
load_dotenv(override=True)

from rich.console import Console
from rich.table import Table
from rich import box
from data.signals import generate_signals
from store.vector_store import get_store
from graph import canary_graph

console = Console()


def main():
    console.rule("[bold purple]CANARY — Supply Chain Intelligence[/bold purple]")

    console.print("Generating signals and indexing...")
    df    = generate_signals(n=80)
    store = get_store()
    store.ingest(df)
    console.print(f"[green]Ingested {len(df)} signals[/green]\n")

    suppliers = df["supplier"].unique().tolist()

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold")
    table.add_column("Supplier",       style="cyan")
    table.add_column("Gate",           justify="center")
    table.add_column("Confidence",     justify="center")
    table.add_column("Primary action")

    for supplier in suppliers:
        console.print(f"Analysing [bold]{supplier}[/bold]...")
        result = canary_graph.invoke({
            "supplier": supplier,
            "result":   {},
            "error":    None,
        })

        if result.get("error"):
            console.print(f"[red]Error: {result['error']}[/red]")
            continue

        gate   = result["result"]["gate"]
        conf   = result["result"]["synthesis"]["overall_confidence"]
        action = result["result"]["synthesis"]["primary_action"]

        gate_color = {"AUTO_EXECUTE": "green", "HUMAN_REVIEW": "yellow", "ALERT_ONLY": "dim"}.get(gate, "white")
        conf_color = "green" if conf >= 0.85 else "yellow" if conf >= 0.60 else "dim"

        table.add_row(
            supplier,
            f"[{gate_color}]{gate}[/{gate_color}]",
            f"[{conf_color}]{conf:.2f}[/{conf_color}]",
            action[:70] + ("..." if len(action) > 70 else ""),
        )

    console.print(table)


if __name__ == "__main__":
    main()
