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

from config import MODELS, DEFAULT_MODEL, SETUPS, DEFAULT_SETUP
from agents import LiteralistAgent, ContextualistAgent, StatisticianAgent
from debate.protocol import DebateProtocol, SingleAgentBaseline
from debate.verdict import VerdictSynthesizer
from debate.crew import FactCheckCrew, SingleAgentCrewBaseline
from utils.display import (
    console,
    print_welcome,
    print_case_header,
    print_claim_vs_truth,
    print_agents_intro,
    print_agent_speech,
    print_debate_round,
    print_verdict_box,
)


AGENT_CLASSES = {
    "literalist": LiteralistAgent,
    "contextualist": ContextualistAgent,
    "statistician": StatisticianAgent,
}


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
  python main.py --case 1                    Run case 1 with CrewAI jury (default)
  python main.py --case all                  Run all cases
  python main.py --case 1 --setup single     Run with single agent baseline
  python main.py --case 1 --setup crew-jury  Run with CrewAI jury
  python main.py --compare --case 2          Compare all setups on case 2
  python main.py --case 3 --model full       Use GPT-4o for case 3

Available setups:
  single          - Single agent baseline (no jury)
  jury-vote       - 3-agent jury with majority vote
  jury-llm        - 3-agent jury with LLM synthesis
  jury-deliberate - 3-agent jury with deliberation round
  crew-single     - Single agent using CrewAI
  crew-jury       - 3-agent CrewAI jury with Judge synthesis (default)
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
        choices=["mini", "full", "cheap"],
        default=DEFAULT_MODEL,
        help="Model: 'mini' for gpt-4.1-mini, 'full' for gpt-4.1"
    )

    parser.add_argument(
        "--setup",
        type=str,
        choices=list(SETUPS.keys()),
        default=DEFAULT_SETUP,
        help="Which setup to use"
    )

    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare all setups on the selected case(s)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed agent reasoning"
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


def create_agents(agent_names: list[str], model: str) -> list:
    """Create agent instances from names."""
    return [AGENT_CLASSES[name](model=model) for name in agent_names]


def run_single_setup(case: dict, setup_name: str, model_name: str, verbose: bool) -> dict:
    """Run a single setup on a case and return results."""
    setup = SETUPS[setup_name]
    model = MODELS[model_name]
    use_crewai = setup.get("use_crewai", False)

    if use_crewai:
        # CrewAI-based execution
        if setup["mode"] == "single":
            crew_baseline = SingleAgentCrewBaseline(model=model)
            result = crew_baseline.analyze(case["claim"], case["truth"], case["id"])

            return {
                "setup": setup_name,
                "verdict": result.final_verdict,
                "confidence": result.final_confidence,
                "reasoning": result.final_reasoning,
                "agents_used": 1,
                "debate_result": result,
            }
        else:
            # Multi-agent CrewAI jury
            crew = FactCheckCrew(model=model, mode=setup["mode"])
            result = crew.run_debate(case["claim"], case["truth"], case["id"])

            return {
                "setup": setup_name,
                "verdict": result.final_verdict,
                "confidence": result.final_confidence,
                "reasoning": result.final_reasoning,
                "mutation_type": result.mutation_type,
                "dissenting": result.dissenting_opinions,
                "agents_used": 3,
                "debate_result": result,
            }
    else:
        # Original implementation
        if setup["mode"] == "single":
            # Single agent baseline
            baseline = SingleAgentBaseline(model=model)
            result = baseline.analyze(case["claim"], case["truth"], case["id"])

            verdict = result.initial_verdicts[0]
            return {
                "setup": setup_name,
                "verdict": verdict.verdict,
                "confidence": verdict.confidence,
                "reasoning": verdict.reasoning,
                "agents_used": 1,
                "debate_result": result,
            }
        else:
            # Multi-agent jury
            agents = create_agents(setup["agents"], model)

            protocol = DebateProtocol(
                agents=agents,
                mode=setup["mode"],
                max_rounds=setup.get("rounds", 0),
                parallel=True
            )

            debate_result = protocol.run_debate(case["claim"], case["truth"], case["id"])

            synthesizer = VerdictSynthesizer(
                strategy=setup["synthesis"],
                model=model
            )

            final = synthesizer.synthesize(debate_result)

            return {
                "setup": setup_name,
                "verdict": final.verdict,
                "confidence": final.confidence,
                "reasoning": final.reasoning,
                "mutation_type": final.mutation_type,
                "dissenting": final.dissenting_opinions,
                "agents_used": len(agents),
                "debate_result": debate_result,
                "final_verdict": final,
            }


def display_result(result: dict, verbose: bool):
    """Display the result of a setup run."""
    debate_result = result["debate_result"]

    # Show individual agent verdicts
    if result["agents_used"] > 1:
        console.print("\n[bold]Agent Verdicts:[/bold]")
        for verdict in debate_result.initial_verdicts:
            print_agent_speech(
                agent_name=verdict.agent_name,
                color={"Literalist": "red", "Contextualist": "blue", "Statistician": "green"}.get(verdict.agent_name, "white"),
                message=verdict.reasoning if verbose else verdict.reasoning[:200] + "..." if len(verdict.reasoning) > 200 else verdict.reasoning,
                verdict=verdict.verdict,
                confidence=verdict.confidence
            )

        # Show debate rounds if any
        if debate_result.debate_rounds:
            for round in debate_result.debate_rounds:
                print_debate_round(round.round_number)
                for resp in round.responses:
                    print_agent_speech(
                        agent_name=resp["agent"],
                        color=resp["color"],
                        message=resp["response"],
                    )
    else:
        # Single agent
        verdict = debate_result.initial_verdicts[0]
        print_agent_speech(
            agent_name="Single Agent",
            color="yellow",
            message=verdict.reasoning if verbose else verdict.reasoning[:300] + "..." if len(verdict.reasoning) > 300 else verdict.reasoning,
            verdict=verdict.verdict,
            confidence=verdict.confidence
        )

    # Show final verdict
    print_verdict_box(
        verdict=result["verdict"],
        confidence=result["confidence"],
        reasoning=result["reasoning"][:300] + "..." if len(result["reasoning"]) > 300 else result["reasoning"],
        mutation_type=result.get("mutation_type")
    )


def run_case(case: dict, setup_name: str, model_name: str, verbose: bool) -> dict:
    """Run a single case with the specified setup."""
    setup = SETUPS[setup_name]
    use_crewai = setup.get("use_crewai", False)

    print_case_header(case["id"], case["name"], case["mutation_type"])
    print_claim_vs_truth(case["claim"], case["truth"])

    console.print(f"[dim]Setup: {setup_name} - {setup['description']}[/dim]\n")

    # Show agents if multi-agent (only for non-CrewAI setups since CrewAI handles this internally)
    if setup["mode"] != "single" and not use_crewai:
        agents = create_agents(setup["agents"], MODELS[model_name])
        print_agents_intro(agents)
    elif setup["mode"] != "single" and use_crewai:
        console.print("[dim]Using CrewAI agents: Literalist, Contextualist, Statistician, Judge[/dim]\n")

    # Run the analysis
    with console.status("[bold green]Agents deliberating..."):
        result = run_single_setup(case, setup_name, model_name, verbose)

    display_result(result, verbose)

    return result


def compare_setups(case: dict, model_name: str, verbose: bool):
    """Compare all setups on a single case."""
    print_case_header(case["id"], case["name"], case["mutation_type"])
    print_claim_vs_truth(case["claim"], case["truth"])

    console.print("[bold magenta]Comparing all setups...[/bold magenta]\n")

    results = []
    for setup_name in SETUPS:
        console.rule(f"[bold]{setup_name}[/bold]: {SETUPS[setup_name]['description']}")

        with console.status(f"[bold green]Running {setup_name}..."):
            result = run_single_setup(case, setup_name, model_name, verbose)

        results.append(result)

        # Brief display
        console.print(f"  Verdict: [bold]{result['verdict'].upper()}[/bold] ({result['confidence']:.0%} confidence)")
        if result.get("mutation_type"):
            console.print(f"  Type: {result['mutation_type']}")
        console.print()

    # Summary table
    console.print("\n[bold]Comparison Summary:[/bold]")
    from rich.table import Table
    table = Table()
    table.add_column("Setup", style="cyan")
    table.add_column("Verdict", style="bold")
    table.add_column("Confidence")
    table.add_column("Agents")

    for r in results:
        verdict_style = {"faithful": "green", "mutation": "red", "uncertain": "yellow"}.get(r["verdict"], "white")
        table.add_row(
            r["setup"],
            f"[{verdict_style}]{r['verdict'].upper()}[/{verdict_style}]",
            f"{r['confidence']:.0%}",
            str(r["agents_used"])
        )

    console.print(table)

    # Check agreement
    verdicts = [r["verdict"] for r in results]
    if len(set(verdicts)) == 1:
        console.print(f"\n[green]All setups agree: {verdicts[0].upper()}[/green]")
    else:
        console.print(f"\n[yellow]Setups disagree! Verdicts: {', '.join(verdicts)}[/yellow]")

    return results


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

    if args.compare:
        console.print(f"[dim]Comparing all setups on {len(case_ids)} case(s)[/dim]\n")
    else:
        console.print(f"[dim]Setup: {args.setup}[/dim]")
        console.print(f"[dim]Running {len(case_ids)} case(s)[/dim]\n")

    # Run each case
    for case_id in case_ids:
        case = next(c for c in cases if c["id"] == case_id)

        if args.compare:
            compare_setups(case, args.model, args.verbose)
        else:
            run_case(case, args.setup, args.model, args.verbose)

        if case_id != case_ids[-1]:
            console.print("\n" + "=" * 70 + "\n")

    console.print("\n[bold green]Done![/bold green]")


if __name__ == "__main__":
    main()
