"""Pretty display utilities for demo using Rich library."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.markdown import Markdown
from rich import box

console = Console()


def print_case_header(case_id: int, case_name: str, mutation_type: str) -> None:
    """Print a styled header for a case."""
    console.print()
    console.rule(f"[bold cyan]Case {case_id}: {case_name}[/bold cyan]")
    console.print(f"[dim]Mutation Type: {mutation_type}[/dim]")
    console.print()


def print_claim_vs_truth(claim: str, truth: str) -> None:
    """Display the claim and truth side by side."""
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold")
    table.add_column("Claim", style="yellow", width=45)
    table.add_column("Source Truth", style="green", width=45)
    table.add_row(claim, truth)
    console.print(table)
    console.print()


def print_agent_speech(
    agent_name: str,
    color: str,
    message: str,
    verdict: str = None,
    confidence: float = None
) -> None:
    """Print an agent's statement with colored name badge."""
    # Create the name badge
    badge = Text(f" {agent_name} ", style=f"bold white on {color}")

    # Add verdict indicator if provided
    verdict_text = ""
    if verdict:
        verdict_emoji = {
            "faithful": "[green]FAITHFUL[/green]",
            "mutation": "[red]MUTATION[/red]",
            "uncertain": "[yellow]UNCERTAIN[/yellow]"
        }.get(verdict.lower(), verdict)
        confidence_str = f" ({confidence:.0%})" if confidence else ""
        verdict_text = f" | {verdict_emoji}{confidence_str}"

    console.print(badge, end="")
    console.print(verdict_text)
    console.print(Panel(message, border_style=color, padding=(0, 1)))


def print_debate_round(round_number: int) -> None:
    """Print a debate round separator."""
    console.print()
    console.rule(f"[bold magenta]Debate Round {round_number}[/bold magenta]")
    console.print()


def print_verdict_box(
    verdict: str,
    confidence: float,
    reasoning: str,
    mutation_type: str = None
) -> None:
    """Print the final verdict in a prominent box."""
    # Determine styling based on verdict
    if verdict.lower() == "faithful":
        border_style = "green"
        verdict_display = "[bold green]FAITHFUL[/bold green]"
        icon = "checkmark"
    elif verdict.lower() == "mutation":
        border_style = "red"
        verdict_display = "[bold red]MUTATION DETECTED[/bold red]"
        icon = "warning"
    else:
        border_style = "yellow"
        verdict_display = "[bold yellow]UNCERTAIN[/bold yellow]"
        icon = "question"

    # Build content
    content_lines = [
        f"Verdict: {verdict_display}",
        f"Confidence: [bold]{confidence:.0%}[/bold]",
    ]

    if mutation_type:
        content_lines.append(f"Type: [italic]{mutation_type}[/italic]")

    content_lines.append("")
    content_lines.append(f"[dim]Reasoning:[/dim] {reasoning}")

    content = "\n".join(content_lines)

    console.print()
    console.print(Panel(
        content,
        title="[bold]JURY VERDICT[/bold]",
        border_style=border_style,
        box=box.DOUBLE,
        padding=(1, 2)
    ))


def print_welcome() -> None:
    """Print welcome banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███████╗ █████╗  ██████╗████████╗████████╗██████╗  █████╗   ║
║   ██╔════╝██╔══██╗██╔════╝╚══██╔══╝╚══██╔══╝██╔══██╗██╔══██╗  ║
║   █████╗  ███████║██║        ██║      ██║   ██████╔╝███████║  ║
║   ██╔══╝  ██╔══██║██║        ██║      ██║   ██╔══██╗██╔══██║  ║
║   ██║     ██║  ██║╚██████╗   ██║      ██║   ██║  ██║██║  ██║  ║
║   ╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝  ║
║                                                               ║
║        Multi-Agent Fact Verification System                   ║
║        A Jury of AI Agents for Truth Detection                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="bold cyan")


def print_agents_intro(agents: list) -> None:
    """Print introduction of the agent jury."""
    console.print("\n[bold]THE JURY:[/bold]\n")
    for agent in agents:
        badge = Text(f" {agent.name} ", style=f"bold white on {agent.color}")
        console.print(badge, end=" ")
        console.print(f"[dim]{agent.role_description}[/dim]")
    console.print()
