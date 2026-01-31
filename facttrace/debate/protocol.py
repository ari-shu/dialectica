"""Debate protocol that orchestrates multi-agent deliberation."""

from dataclasses import dataclass, field
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.base_agent import BaseAgent, AgentVerdict


@dataclass
class DebateRound:
    """A single round of debate."""
    round_number: int
    responses: list[dict] = field(default_factory=list)  # {"agent": str, "response": str}


@dataclass
class DebateResult:
    """Complete result of a debate session."""
    case_id: int
    claim: str
    truth: str
    initial_verdicts: list[AgentVerdict]
    debate_rounds: list[DebateRound]
    final_verdict: Optional[str] = None
    final_confidence: float = 0.0
    final_reasoning: str = ""


class DebateProtocol:
    """
    Orchestrates the multi-agent debate process.

    Supports multiple modes:
    - "one-shot": Each agent analyzes independently, then majority vote
    - "deliberation": Agents see each other's verdicts and can respond
    """

    def __init__(
        self,
        agents: list[BaseAgent],
        mode: str = "one-shot",
        max_rounds: int = 1,
        parallel: bool = True
    ):
        self.agents = agents
        self.mode = mode
        self.max_rounds = max_rounds
        self.parallel = parallel

    def run_debate(self, claim: str, truth: str, case_id: int = 0) -> DebateResult:
        """
        Run a full debate session on a claim.

        Args:
            claim: The claim to verify
            truth: The source truth
            case_id: Identifier for the case

        Returns:
            DebateResult with all verdicts and discussion
        """
        # Phase 1: Collect initial verdicts from all agents
        initial_verdicts = self._collect_initial_verdicts(claim, truth)

        debate_rounds = []

        # Phase 2: Optional deliberation rounds
        if self.mode == "deliberation" and self.max_rounds > 0:
            for round_num in range(1, self.max_rounds + 1):
                debate_round = self._run_debate_round(
                    round_num, claim, truth, initial_verdicts
                )
                debate_rounds.append(debate_round)

        return DebateResult(
            case_id=case_id,
            claim=claim,
            truth=truth,
            initial_verdicts=initial_verdicts,
            debate_rounds=debate_rounds
        )

    def _collect_initial_verdicts(self, claim: str, truth: str) -> list[AgentVerdict]:
        """Have each agent independently analyze the claim."""
        verdicts = []

        if self.parallel and len(self.agents) > 1:
            # Run agents in parallel for speed
            with ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
                future_to_agent = {
                    executor.submit(agent.analyze, claim, truth): agent
                    for agent in self.agents
                }
                for future in as_completed(future_to_agent):
                    try:
                        verdict = future.result()
                        verdicts.append(verdict)
                    except Exception as e:
                        agent = future_to_agent[future]
                        verdicts.append(AgentVerdict(
                            agent_name=agent.name,
                            verdict="uncertain",
                            confidence=0.0,
                            reasoning=f"Error: {str(e)}",
                            evidence=[]
                        ))
        else:
            # Run sequentially
            for agent in self.agents:
                try:
                    verdict = agent.analyze(claim, truth)
                    verdicts.append(verdict)
                except Exception as e:
                    verdicts.append(AgentVerdict(
                        agent_name=agent.name,
                        verdict="uncertain",
                        confidence=0.0,
                        reasoning=f"Error: {str(e)}",
                        evidence=[]
                    ))

        return verdicts

    def _run_debate_round(
        self,
        round_num: int,
        claim: str,
        truth: str,
        verdicts: list[AgentVerdict]
    ) -> DebateRound:
        """Run a single round of debate where agents respond to each other."""
        responses = []

        for agent in self.agents:
            try:
                response = agent.respond_to(verdicts, claim, truth)
                responses.append({
                    "agent": agent.name,
                    "color": agent.color,
                    "response": response
                })
            except Exception as e:
                responses.append({
                    "agent": agent.name,
                    "color": agent.color,
                    "response": f"[Error generating response: {str(e)}]"
                })

        return DebateRound(round_number=round_num, responses=responses)


class SingleAgentBaseline:
    """
    Single agent baseline for comparison.
    Uses one generic agent to make the decision.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        from openai import OpenAI
        from config import OPENAI_API_KEY
        self.model = model
        self._client = OpenAI(api_key=OPENAI_API_KEY)

    def analyze(self, claim: str, truth: str, case_id: int = 0) -> DebateResult:
        """Run single-agent analysis."""
        import json
        import re

        prompt = f"""Analyze whether the following CLAIM is a faithful representation of the SOURCE TRUTH, or if it's a mutation (distortion, exaggeration, missing context, etc.).

SOURCE TRUTH:
{truth}

CLAIM:
{claim}

Consider:
1. Factual accuracy (numbers, dates, specific details)
2. Context preservation (caveats, qualifiers, implications)
3. Statistical/numerical framing

Respond with a JSON object:
{{
    "verdict": "faithful" | "mutation" | "uncertain",
    "confidence": <float 0.0-1.0>,
    "reasoning": "<your detailed reasoning>",
    "evidence": ["<evidence point 1>", "<evidence point 2>"]
}}"""

        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert fact-checker analyzing whether claims faithfully represent their sources."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        content = response.choices[0].message.content

        # Parse response
        try:
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
                verdict = AgentVerdict(
                    agent_name="Single Agent",
                    verdict=data.get("verdict", "uncertain").lower(),
                    confidence=float(data.get("confidence", 0.5)),
                    reasoning=data.get("reasoning", "No reasoning"),
                    evidence=data.get("evidence", [])
                )
            else:
                raise ValueError("No JSON found")
        except:
            verdict = AgentVerdict(
                agent_name="Single Agent",
                verdict="uncertain",
                confidence=0.5,
                reasoning=content[:500],
                evidence=[]
            )

        return DebateResult(
            case_id=case_id,
            claim=claim,
            truth=truth,
            initial_verdicts=[verdict],
            debate_rounds=[],
            final_verdict=verdict.verdict,
            final_confidence=verdict.confidence,
            final_reasoning=verdict.reasoning
        )
