"""Statistician Agent - focuses on numerical accuracy and framing."""

from agents.base_agent import BaseAgent, AgentVerdict


class StatisticianAgent(BaseAgent):
    """
    The Statistician checks numerical claims and statistical framing.

    This agent focuses on:
    - Numerical accuracy and rounding issues
    - Statistical framing (e.g., "more than" vs "exactly")
    - Temporal precision in data claims
    - Whether numbers are presented misleadingly
    """

    @property
    def name(self) -> str:
        return "Statistician"

    @property
    def role_description(self) -> str:
        return (
            "I analyze numerical claims and their framing. I check for "
            "rounding errors, misleading comparisons, temporal precision "
            "issues, and whether statistics are presented fairly."
        )

    @property
    def color(self) -> str:
        return "green"

    def analyze(self, claim: str, truth: str) -> AgentVerdict:
        """Analyze claim for numerical and statistical accuracy."""
        # TODO: Implement LLM-based analysis
        raise NotImplementedError("Statistician analysis not yet implemented")

    def respond_to(self, other_agent_argument: str, context: dict) -> str:
        """Respond to another agent's argument."""
        # TODO: Implement debate response
        raise NotImplementedError("Statistician debate response not yet implemented")
