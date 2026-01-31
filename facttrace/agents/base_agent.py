"""Abstract base class for all fact-checking agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentVerdict:
    """Structured verdict from an agent."""
    agent_name: str
    verdict: str  # "faithful", "mutation", "uncertain"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    evidence: list[str]


class BaseAgent(ABC):
    """Abstract base class for fact-checking agents in the jury."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent's display name."""
        pass

    @property
    @abstractmethod
    def role_description(self) -> str:
        """Description of the agent's role and expertise."""
        pass

    @property
    @abstractmethod
    def color(self) -> str:
        """Color for display purposes (rich color name)."""
        pass

    @abstractmethod
    def analyze(self, claim: str, truth: str) -> AgentVerdict:
        """
        Analyze a claim against the source truth.

        Args:
            claim: The claim to verify
            truth: The source/ground truth text

        Returns:
            AgentVerdict with the agent's assessment
        """
        pass

    @abstractmethod
    def respond_to(self, other_agent_argument: str, context: dict) -> str:
        """
        Respond to another agent's argument during debate.

        Args:
            other_agent_argument: The argument made by another agent
            context: Dict containing claim, truth, and debate history

        Returns:
            The agent's response/rebuttal
        """
        pass

    def _call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call the LLM with the given prompt.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt

        Returns:
            The LLM response text
        """
        # TODO: Implement actual LLM call
        raise NotImplementedError("LLM calls not yet implemented")
