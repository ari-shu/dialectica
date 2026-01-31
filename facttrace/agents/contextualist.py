"""Contextualist Agent - focuses on missing context and implications."""

from agents.base_agent import BaseAgent, AgentVerdict


class ContextualistAgent(BaseAgent):
    """
    The Contextualist checks for missing or distorted context.

    This agent focuses on:
    - Important caveats or qualifiers that were omitted
    - Context that changes the meaning of facts
    - Implications that differ between claim and source
    """

    @property
    def name(self) -> str:
        return "Contextualist"

    @property
    def role_description(self) -> str:
        return (
            "I examine whether important context is preserved. I look for "
            "missing caveats, omitted qualifiers, and contextual information "
            "that changes the meaning or implications of the facts."
        )

    @property
    def color(self) -> str:
        return "blue"

    def analyze(self, claim: str, truth: str) -> AgentVerdict:
        """Analyze claim for contextual faithfulness."""
        # TODO: Implement LLM-based analysis
        raise NotImplementedError("Contextualist analysis not yet implemented")

    def respond_to(self, other_agent_argument: str, context: dict) -> str:
        """Respond to another agent's argument."""
        # TODO: Implement debate response
        raise NotImplementedError("Contextualist debate response not yet implemented")
