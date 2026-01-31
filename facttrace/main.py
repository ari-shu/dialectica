#!/usr/bin/env python3
"""
FactTrace - Multi-Agent Fact Verification System

A jury of AI agents that debates whether claims are faithful
representations of source facts, or mutations.
"""

import argparse
import json
import sys
from pathlib import Path

from config import MODELS, DEFAULT_MODEL
from agents import LiteralistAgent, ContextualistAgent, StatisticianAgent
from debate.protocol import DebateProtocol
from debate.verdict import VerdictSynthesizer
from utils.display import (
    console,
    print_welcome,
    print_case_header,
    print_claim_vs_truth,
    print_agents_intro,
    print_verdict_box,
)


def load_cases(data_path: Path) -> list[dict]:
    """Load cases from JSON file."""
    with open(data_path) as f:
        data = json.load(f)
    return data["cases"]


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="FactTrace: Multi-Agent Fact Verification System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --case 1              Run case 1
  python main.py --case all            Run all cases
  python main.py --case 3 --model full Use GPT-4o for case 3
  python main.py --case 2 --verbose    Show detailed debate
        """
    )

    parser.add_argument(
        "--case",
        type=str,
        default="1",
        help="Case number (1-5) or 'all' to run all cases"
    )

    parser.add_argument(
        "--model",
        type=str,
        choices=["mini", "full"],
        default=DEFAULT_MODEL,
        help="Model to use: 'mini' for gpt-4o-mini, 'full' for gpt-4o"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed debate rounds"
    )

    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Skip the welcome banner"
    )

    return parser.parse_args()


def get_case_ids(case_arg: str, total_cases: int) -> list[int]:
    """Parse case argument to list of case IDs."""
    if case_arg.lower() == "all":
        return list(range(1, total_cases + 1))

    try:
        case_id = int(case_arg)
        if 1 <= case_id <= total_cases:
            return [case_id]
        else:
            console.print(f"[red]Error: Case {case_id} not found. Choose 1-{total_cases}.[/red]")
            sys.exit(1)
    except ValueError:
        console.print(f"[red]Error: Invalid case '{case_arg}'. Use 1-{total_cases} or 'all'.[/red]")
        sys.exit(1)


def run_case(case: dict, model: str, verbose: bool) -> None:
    """Run the debate for a single case."""
    print_case_header(case["id"], case["name"], case["mutation_type"])
    print_claim_vs_truth(case["claim"], case["truth"])

    # Initialize agents
    agents = [
        LiteralistAgent(model=MODELS[model]),
        ContextualistAgent(model=MODELS[model]),
        StatisticianAgent(model=MODELS[model]),
    ]

    print_agents_intro(agents)

    # TODO: Run debate protocol here
    console.print("[yellow]TODO: Run debate protocol here[/yellow]")
    console.print("[dim]Debate logic not yet implemented[/dim]")

    # TODO: Display final verdict
    console.print("\n[yellow]TODO: Display final verdict here[/yellow]")


def main():
    """Main entry point."""
    args = parse_args()

    # Show welcome banner
    if not args.no_banner:
        print_welcome()

    # Load cases
    data_path = Path(__file__).parent / "data" / "cases.json"
    cases = load_cases(data_path)

    # Determine which cases to run
    case_ids = get_case_ids(args.case, len(cases))

    console.print(f"[dim]Using model: {MODELS[args.model]}[/dim]")
    console.print(f"[dim]Running {len(case_ids)} case(s)[/dim]")

    # Run each case
    for case_id in case_ids:
        case = next(c for c in cases if c["id"] == case_id)
        run_case(case, args.model, args.verbose)

        if case_id != case_ids[-1]:
            console.print("\n" + "=" * 60 + "\n")

    console.print("\n[bold green]Done![/bold green]")


if __name__ == "__main__":
    main()
