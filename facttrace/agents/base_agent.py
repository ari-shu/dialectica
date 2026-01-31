"""Abstract base class for all fact-checking agents."""

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Optional

from openai import OpenAI
from config import OPENAI_API_KEY


@dataclass
class AgentVerdict:
    """Structured verdict from an agent."""
    agent_name: str
    verdict: str  # "faithful", "mutation", "uncertain"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    evidence: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


class BaseAgent(ABC):
    """Abstract base class for fact-checking agents in the jury."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self._client = OpenAI(api_key=OPENAI_API_KEY)

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

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """The system prompt defining this agent's perspective."""
        pass

    def analyze(self, claim: str, truth: str) -> AgentVerdict:
        """
        Analyze a claim against the source truth.

        Args:
            claim: The claim to verify
            truth: The source/ground truth text

        Returns:
            AgentVerdict with the agent's assessment
        """
        prompt = f"""Analyze whether the following CLAIM is a faithful representation of the SOURCE TRUTH, or if it's a mutation (distortion, exaggeration, missing context, etc.).

SOURCE TRUTH:
{truth}

CLAIM:
{claim}

Respond with a JSON object containing:
{{
    "verdict": "faithful" | "mutation" | "uncertain",
    "confidence": <float 0.0-1.0>,
    "reasoning": "<your detailed reasoning>",
    "evidence": ["<specific evidence point 1>", "<specific evidence point 2>", ...]
}}

Focus on your specific expertise as {self.name}. Be precise and cite specific differences or matches."""

        response = self._call_llm(prompt, self.system_prompt)
        return self._parse_verdict(response)

    def respond_to(self, other_verdicts: list['AgentVerdict'], claim: str, truth: str) -> str:
        """
        Respond to other agents' verdicts during debate.

        Args:
            other_verdicts: Verdicts from other agents
            claim: The original claim
            truth: The source truth

        Returns:
            The agent's response/rebuttal
        """
        verdicts_text = "\n\n".join([
            f"**{v.agent_name}** ({v.verdict}, {v.confidence:.0%} confidence):\n{v.reasoning}"
            for v in other_verdicts if v.agent_name != self.name
        ])

        prompt = f"""You previously analyzed this case. Now review your colleagues' opinions and provide a brief response.

SOURCE TRUTH: {truth}

CLAIM: {claim}

OTHER AGENTS' VERDICTS:
{verdicts_text}

As {self.name}, do you:
1. Agree with any points raised?
2. Disagree with any conclusions?
3. Want to update your assessment based on new perspectives?

Keep your response concise (2-3 sentences). Focus on the most important point of agreement or disagreement."""

        return self._call_llm(prompt, self.system_prompt)

    def _call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call the LLM with the given prompt.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt

        Returns:
            The LLM response text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        return response.choices[0].message.content

    def _parse_verdict(self, response: str) -> AgentVerdict:
        """Parse LLM response into AgentVerdict."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return AgentVerdict(
                    agent_name=self.name,
                    verdict=data.get("verdict", "uncertain").lower(),
                    confidence=float(data.get("confidence", 0.5)),
                    reasoning=data.get("reasoning", "No reasoning provided"),
                    evidence=data.get("evidence", [])
                )
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

        # Fallback: try to parse from text
        verdict = "uncertain"
        if "faithful" in response.lower():
            verdict = "faithful"
        elif "mutation" in response.lower():
            verdict = "mutation"

        return AgentVerdict(
            agent_name=self.name,
            verdict=verdict,
            confidence=0.5,
            reasoning=response[:500],
            evidence=[]
        )
