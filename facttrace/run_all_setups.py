#!/usr/bin/env python3
"""
Run all setups on all cases and save results to a file.

Usage:
    python run_all_setups.py
"""

import json
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import MODELS, SETUPS, DEFAULT_MODEL
from agents import LiteralistAgent, ContextualistAgent, StatisticianAgent
from debate.protocol import DebateProtocol, SingleAgentBaseline
from debate.verdict import VerdictSynthesizer
from debate.crew import FactCheckCrew, SingleAgentCrewBaseline

console = Console()

# Configuration
MODEL_NAME = DEFAULT_MODEL
OUTPUT_FILE = "results.json"

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


def create_agents(agent_names: list[str], model: str) -> list:
    """Create agent instances from names."""
    return [AGENT_CLASSES[name](model=model) for name in agent_names]


def run_setup(case: dict, setup_name: str, model: str) -> dict:
    """Run a single setup on a case and return results."""
    setup = SETUPS[setup_name]
    use_crewai = setup.get("use_crewai", False)

    start_time = datetime.now()

    try:
        if use_crewai:
            if setup["mode"] == "single":
                crew_baseline = SingleAgentCrewBaseline(model=model)
                result = crew_baseline.analyze(case["claim"], case["truth"], case["id"])

                return {
                    "setup": setup_name,
                    "verdict": result.final_verdict,
                    "confidence": result.final_confidence,
                    "reasoning": result.final_reasoning,
                    "mutation_type": result.mutation_type,
                    "agents_used": 1,
                    "duration_seconds": (datetime.now() - start_time).total_seconds(),
                    "error": None,
                }
            else:
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
                    "individual_verdicts": [
                        {
                            "agent": v.agent_name,
                            "verdict": v.verdict,
                            "confidence": v.confidence,
                            "reasoning": v.reasoning,
                        }
                        for v in result.initial_verdicts
                    ],
                    "duration_seconds": (datetime.now() - start_time).total_seconds(),
                    "error": None,
                }
        else:
            if setup["mode"] == "single":
                baseline = SingleAgentBaseline(model=model)
                result = baseline.analyze(case["claim"], case["truth"], case["id"])
                verdict = result.initial_verdicts[0]

                return {
                    "setup": setup_name,
                    "verdict": verdict.verdict,
                    "confidence": verdict.confidence,
                    "reasoning": verdict.reasoning,
                    "mutation_type": None,
                    "agents_used": 1,
                    "duration_seconds": (datetime.now() - start_time).total_seconds(),
                    "error": None,
                }
            else:
                agents = create_agents(setup["agents"], model)
                protocol = DebateProtocol(
                    agents=agents,
                    mode=setup["mode"],
                    max_rounds=setup.get("rounds", 0),
                    parallel=True
                )
                debate_result = protocol.run_debate(case["claim"], case["truth"], case["id"])

                synthesizer = VerdictSynthesizer(strategy=setup["synthesis"], model=model)
                final = synthesizer.synthesize(debate_result)

                return {
                    "setup": setup_name,
                    "verdict": final.verdict,
                    "confidence": final.confidence,
                    "reasoning": final.reasoning,
                    "mutation_type": final.mutation_type,
                    "dissenting": final.dissenting_opinions,
                    "agents_used": len(agents),
                    "individual_verdicts": [
                        {
                            "agent": v.agent_name,
                            "verdict": v.verdict,
                            "confidence": v.confidence,
                            "reasoning": v.reasoning,
                        }
                        for v in debate_result.initial_verdicts
                    ],
                    "duration_seconds": (datetime.now() - start_time).total_seconds(),
                    "error": None,
                }
    except Exception as e:
        return {
            "setup": setup_name,
            "verdict": "error",
            "confidence": 0.0,
            "reasoning": str(e),
            "mutation_type": None,
            "agents_used": 0,
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "error": str(e),
        }


def run_all(cases: list[dict], model_name: str) -> dict:
    """Run all setups on all cases."""
    model = MODELS[model_name]
    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "model_name": model_name,
            "setups": list(SETUPS.keys()),
            "total_cases": len(cases),
        },
        "cases": []
    }

    total_runs = len(cases) * len(SETUPS)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running experiments...", total=total_runs)

        for case in cases:
            case_result = {
                "case_id": case["id"],
                "case_name": case["name"],
                "mutation_type": case["mutation_type"],
                "claim": case["claim"],
                "truth": case["truth"],
                "setups": []
            }

            for setup_name in SETUPS:
                progress.update(task, description=f"Case {case['id']} - {setup_name}")

                setup_result = run_setup(case, setup_name, model)
                case_result["setups"].append(setup_result)

                progress.advance(task)

            results["cases"].append(case_result)

    return results


def print_summary(results: dict):
    """Print a summary table of results."""
    console.print("\n[bold]Results Summary[/bold]\n")

    for case_data in results["cases"]:
        console.print(f"[bold cyan]Case {case_data['case_id']}: {case_data['case_name']}[/bold cyan]")
        console.print(f"[dim]Expected: {case_data['mutation_type']}[/dim]\n")

        table = Table()
        table.add_column("Setup", style="cyan")
        table.add_column("Verdict", style="bold")
        table.add_column("Confidence")
        table.add_column("Duration")
        table.add_column("Agents")

        for setup in case_data["setups"]:
            verdict_style = {
                "faithful": "green",
                "mutation": "red",
                "uncertain": "yellow",
                "error": "magenta"
            }.get(setup["verdict"], "white")

            table.add_row(
                setup["setup"],
                f"[{verdict_style}]{setup['verdict'].upper()}[/{verdict_style}]",
                f"{setup['confidence']:.0%}",
                f"{setup['duration_seconds']:.1f}s",
                str(setup["agents_used"])
            )

        console.print(table)
        console.print()


def main():
    # Load cases
    data_path = Path(__file__).parent / "data" / "cases.json"
    cases = load_cases(data_path)

    console.print(f"[bold]FactTrace - Running All Setups[/bold]")
    console.print(f"Model: {MODELS[MODEL_NAME]}")
    console.print(f"Cases: {len(cases)}")
    console.print(f"Setups: {len(SETUPS)}")
    console.print(f"Output: {OUTPUT_FILE}\n")

    # Run all experiments
    results = run_all(cases, MODEL_NAME)

    # Save results
    output_path = Path(OUTPUT_FILE)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    console.print(f"\n[green]Results saved to {output_path}[/green]")

    # Print summary
    print_summary(results)

    # Print quick stats
    total_runs = sum(len(c["setups"]) for c in results["cases"])
    total_errors = sum(
        1 for c in results["cases"]
        for s in c["setups"]
        if s["error"]
    )
    total_time = sum(
        s["duration_seconds"]
        for c in results["cases"]
        for s in c["setups"]
    )

    console.print(f"[bold]Stats:[/bold]")
    console.print(f"  Total runs: {total_runs}")
    console.print(f"  Errors: {total_errors}")
    console.print(f"  Total time: {total_time:.1f}s")


if __name__ == "__main__":
    main()
