"""Verdict synthesis from multi-agent debate."""

import json
import re
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI
from config import OPENAI_API_KEY
from agents.base_agent import AgentVerdict
from debate.protocol import DebateResult


@dataclass
class FinalVerdict:
    """The synthesized final verdict."""
    verdict: str  # "faithful", "mutation", "uncertain"
    confidence: float
    reasoning: str
    dissenting_opinions: list[str]
    mutation_type: Optional[str]  # If mutation, what kind


class VerdictSynthesizer:
    """
    Synthesizes a final verdict from the debate results.

    Supports multiple strategies:
    - "majority": Simple majority vote weighted by confidence
    - "unanimous": Requires all agents to agree
    - "llm": Use an LLM to synthesize the final verdict
    """

    def __init__(self, strategy: str = "llm", model: str = "gpt-4o-mini"):
        self.strategy = strategy
        self.model = model
        self._client = OpenAI(api_key=OPENAI_API_KEY)

    def synthesize(self, debate_result: DebateResult) -> FinalVerdict:
        """
        Synthesize a final verdict from debate results.

        Args:
            debate_result: The complete debate result

        Returns:
            FinalVerdict with reasoning
        """
        verdicts = debate_result.initial_verdicts

        if self.strategy == "majority":
            return self._majority_vote(verdicts, debate_result)
        elif self.strategy == "unanimous":
            return self._unanimous_vote(verdicts, debate_result)
        else:  # llm
            return self._llm_synthesis(debate_result)

    def _majority_vote(self, verdicts: list[AgentVerdict], debate_result: DebateResult) -> FinalVerdict:
        """Simple confidence-weighted majority vote."""
        votes = {"faithful": 0.0, "mutation": 0.0, "uncertain": 0.0}

        for v in verdicts:
            votes[v.verdict] += v.confidence

        # Determine winner
        winner = max(votes, key=votes.get)
        total_confidence = sum(votes.values())
        final_confidence = votes[winner] / total_confidence if total_confidence > 0 else 0

        # Collect dissenting opinions
        dissenting = [
            f"{v.agent_name}: {v.reasoning[:100]}..."
            for v in verdicts if v.verdict != winner
        ]

        # Build reasoning
        vote_summary = ", ".join([f"{v.agent_name}={v.verdict}" for v in verdicts])
        reasoning = f"Majority vote ({vote_summary}). Winner: {winner} with weighted score {votes[winner]:.2f}"

        return FinalVerdict(
            verdict=winner,
            confidence=final_confidence,
            reasoning=reasoning,
            dissenting_opinions=dissenting,
            mutation_type=self._identify_mutation_type(debate_result) if winner == "mutation" else None
        )

    def _unanimous_vote(self, verdicts: list[AgentVerdict], debate_result: DebateResult) -> FinalVerdict:
        """Require unanimous agreement."""
        verdict_set = set(v.verdict for v in verdicts)

        if len(verdict_set) == 1:
            # Unanimous
            winner = verdict_set.pop()
            avg_confidence = sum(v.confidence for v in verdicts) / len(verdicts)
            reasoning = f"Unanimous agreement: all {len(verdicts)} agents voted {winner}"
            dissenting = []
        else:
            # No consensus
            winner = "uncertain"
            avg_confidence = 0.5
            reasoning = f"No consensus: agents voted {', '.join(v.verdict for v in verdicts)}"
            dissenting = [f"{v.agent_name}: {v.verdict}" for v in verdicts]

        return FinalVerdict(
            verdict=winner,
            confidence=avg_confidence,
            reasoning=reasoning,
            dissenting_opinions=dissenting,
            mutation_type=self._identify_mutation_type(debate_result) if winner == "mutation" else None
        )

    def _llm_synthesis(self, debate_result: DebateResult) -> FinalVerdict:
        """Use LLM to synthesize final verdict from all agent opinions."""
        # Build summary of all verdicts
        verdicts_text = "\n\n".join([
            f"**{v.agent_name}** (verdict: {v.verdict}, confidence: {v.confidence:.0%}):\n"
            f"Reasoning: {v.reasoning}\n"
            f"Evidence: {'; '.join(v.evidence[:3]) if v.evidence else 'None cited'}"
            for v in debate_result.initial_verdicts
        ])

        # Include debate responses if any
        debate_text = ""
        if debate_result.debate_rounds:
            for round in debate_result.debate_rounds:
                debate_text += f"\n\n--- Debate Round {round.round_number} ---\n"
                for resp in round.responses:
                    debate_text += f"\n{resp['agent']}: {resp['response']}"

        prompt = f"""You are the JUDGE synthesizing a final verdict from a jury of fact-checking agents.

ORIGINAL CASE:
Source Truth: {debate_result.truth}
Claim: {debate_result.claim}

AGENT VERDICTS:
{verdicts_text}
{debate_text}

Based on all agent opinions, synthesize a FINAL VERDICT.

Consider:
- Which agents made the strongest arguments?
- Is there consensus or disagreement?
- What are the key issues identified?

Respond with JSON:
{{
    "verdict": "faithful" | "mutation" | "uncertain",
    "confidence": <float 0.0-1.0>,
    "reasoning": "<synthesis of key points and final judgment>",
    "mutation_type": "<if mutation: 'numerical', 'temporal', 'contextual', 'framing', or null>",
    "dissenting_opinions": ["<brief dissent if any>"]
}}"""

        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an impartial judge synthesizing verdicts from multiple fact-checking experts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent judgments
            max_tokens=800
        )

        content = response.choices[0].message.content

        # Parse response
        try:
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
                return FinalVerdict(
                    verdict=data.get("verdict", "uncertain").lower(),
                    confidence=float(data.get("confidence", 0.5)),
                    reasoning=data.get("reasoning", "No reasoning provided"),
                    dissenting_opinions=data.get("dissenting_opinions", []),
                    mutation_type=data.get("mutation_type")
                )
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

        # Fallback
        return FinalVerdict(
            verdict="uncertain",
            confidence=0.5,
            reasoning=content[:500],
            dissenting_opinions=[],
            mutation_type=None
        )

    def _identify_mutation_type(self, debate_result: DebateResult) -> Optional[str]:
        """Identify mutation type from agent evidence."""
        all_evidence = []
        all_reasoning = []

        for v in debate_result.initial_verdicts:
            all_evidence.extend(v.evidence)
            all_reasoning.append(v.reasoning.lower())

        combined = " ".join(all_reasoning + all_evidence).lower()

        # Simple keyword matching
        if any(word in combined for word in ["date", "temporal", "time", "when", "as of", "after", "before"]):
            return "temporal"
        if any(word in combined for word in ["number", "statistic", "figure", "count", "more than", "less than"]):
            return "numerical"
        if any(word in combined for word in ["context", "caveat", "omit", "missing", "qualifier"]):
            return "contextual"
        if any(word in combined for word in ["frame", "framing", "implication", "meaning", "interpretation"]):
            return "framing"

        return "unspecified"
