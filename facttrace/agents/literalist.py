"""Literalist Agent - focuses on factual accuracy and exact matching."""

from agents.base_agent import BaseAgent, AgentVerdict


class LiteralistAgent(BaseAgent):
    """
    The Literalist checks for exact factual accuracy.

    This agent focuses on:
    - Exact numbers, dates, and quantities
    - Precise wording and terminology
    - Direct contradictions between claim and source
    """

    @property
    def name(self) -> str:
        return "Literalist"

    @property
    def role_description(self) -> str:
        return (
            "I verify exact factual accuracy. I check if numbers, dates, "
            "and specific details in the claim precisely match the source. "
            "Any deviation in hard facts is a potential mutation."
        )

    @property
    def color(self) -> str:
        return "red"

    def analyze(self, claim: str, truth: str) -> AgentVerdict:
        """Analyze claim for literal factual accuracy."""
        # TODO: Implement LLM-based analysis
        raise NotImplementedError("Literalist analysis not yet implemented")

    def respond_to(self, other_agent_argument: str, context: dict) -> str:
        """Respond to another agent's argument."""
        # TODO: Implement debate response
        raise NotImplementedError("Literalist debate response not yet implemented")
