"""CrewAI-based debate orchestration for fact verification."""

import json
import re
from typing import Optional
from dataclasses import dataclass, field

from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

from config import OPENAI_API_KEY
from agents.base_agent import AgentVerdict


@dataclass
class CrewDebateResult:
    """Result from a CrewAI debate session."""
    case_id: int
    claim: str
    truth: str
    initial_verdicts: list[AgentVerdict]
    debate_rounds: list = field(default_factory=list)
    final_verdict: Optional[str] = None
    final_confidence: float = 0.0
    final_reasoning: str = ""
    mutation_type: Optional[str] = None
    dissenting_opinions: list[str] = field(default_factory=list)


def create_literalist_agent(model: str) -> Agent:
    """Create the Literalist agent for exact factual accuracy checking."""
    return Agent(
        role="Literalist Fact-Checker",
        goal="Verify exact factual accuracy by checking if numbers, dates, and specific details precisely match the source",
        backstory="""You are the LITERALIST, a meticulous fact-checker focused on exact accuracy.

Your expertise:
- Detecting numerical discrepancies (wrong numbers, dates, percentages)
- Identifying misquoted or altered wording
- Spotting additions or omissions of specific facts
- Catching temporal errors ("as of" vs "after", specific dates)

Your standards:
- Numbers must match exactly or the rounding must be clearly justified
- Dates and timeframes must be precisely preserved
- Direct quotes or paraphrases must not alter meaning
- "More than X" is NOT the same as "exactly X" or "X"

Be pedantic. Small differences matter. If the claim says "after Feb 13" but the source says "as of Feb 13", that's a significant temporal shift.""",
        llm=LLM(model=model, api_key=OPENAI_API_KEY),
        verbose=False,
        allow_delegation=False,
    )


def create_contextualist_agent(model: str) -> Agent:
    """Create the Contextualist agent for context and implications checking."""
    return Agent(
        role="Contextualist Fact-Checker",
        goal="Examine whether important context is preserved, looking for missing caveats, omitted qualifiers, and contextual information that changes meaning",
        backstory="""You are the CONTEXTUALIST, an expert at detecting missing or distorted context.

Your expertise:
- Identifying omitted caveats and qualifiers
- Detecting when important context changes meaning
- Spotting cherry-picked facts that misrepresent the whole
- Finding missing uncertainty or limitations mentioned in the source

Your standards:
- A fact without its caveat can be misleading even if technically accurate
- Omitting "official figures may not have counted..." changes the reliability implied
- Geographic or demographic context matters ("in China" vs "worldwide")
- Temporal context matters ("as of" implies a snapshot, not ongoing)

You care about the SPIRIT of the truth, not just the letter. A claim can be technically accurate but contextually misleading.""",
        llm=LLM(model=model, api_key=OPENAI_API_KEY),
        verbose=False,
        allow_delegation=False,
    )


def create_statistician_agent(model: str) -> Agent:
    """Create the Statistician agent for numerical claims analysis."""
    return Agent(
        role="Statistician Fact-Checker",
        goal="Analyze numerical claims and their framing, checking for rounding errors, misleading comparisons, and whether statistics are presented fairly",
        backstory="""You are the STATISTICIAN, an expert at analyzing numerical claims and their framing.

Your expertise:
- Evaluating whether rounding is appropriate or misleading
- Detecting subtle numerical manipulations
- Analyzing temporal precision (date shifts, "as of" vs "by")
- Identifying misleading framing of statistics

Your standards:
- "More than 374,000" vs "more than 375,000" - is this rounding acceptable?
- Date shifts (March 23 data attributed to March 24) may seem minor but matter
- Understatements and overstatements in numbers
- Whether numerical precision is preserved appropriately

You balance pedantry with practicality. Minor rounding may be acceptable; shifting dates to inflate numbers is not.""",
        llm=LLM(model=model, api_key=OPENAI_API_KEY),
        verbose=False,
        allow_delegation=False,
    )


def create_judge_agent(model: str) -> Agent:
    """Create the Judge agent for synthesizing final verdict."""
    return Agent(
        role="Chief Judge",
        goal="Synthesize all fact-checker opinions into a final, well-reasoned verdict",
        backstory="""You are the CHIEF JUDGE, responsible for synthesizing the opinions of multiple expert fact-checkers into a final verdict.

Your role:
- Consider all perspectives from the fact-checking jury
- Weigh the evidence and reasoning from each expert
- Identify points of agreement and disagreement
- Render a final verdict with clear justification

You must be fair, thorough, and decisive. Your verdict should reflect the consensus while acknowledging any dissent.""",
        llm=LLM(model=model, api_key=OPENAI_API_KEY),
        verbose=False,
        allow_delegation=False,
    )


def parse_verdict_from_output(output: str, agent_name: str) -> AgentVerdict:
    """Parse an agent's output into an AgentVerdict."""
    try:
        json_match = re.search(r'\{[\s\S]*\}', output)
        if json_match:
            data = json.loads(json_match.group())
            return AgentVerdict(
                agent_name=agent_name,
                verdict=data.get("verdict", "uncertain").lower(),
                confidence=float(data.get("confidence", 0.5)),
                reasoning=data.get("reasoning", "No reasoning provided"),
                evidence=data.get("evidence", [])
            )
    except (json.JSONDecodeError, KeyError, ValueError):
        pass

    # Fallback parsing
    verdict = "uncertain"
    if "faithful" in output.lower():
        verdict = "faithful"
    elif "mutation" in output.lower():
        verdict = "mutation"

    return AgentVerdict(
        agent_name=agent_name,
        verdict=verdict,
        confidence=0.5,
        reasoning=output[:500] if output else "No response",
        evidence=[]
    )


def parse_final_verdict(output: str) -> dict:
    """Parse the judge's final verdict output."""
    try:
        json_match = re.search(r'\{[\s\S]*\}', output)
        if json_match:
            data = json.loads(json_match.group())
            return {
                "verdict": data.get("verdict", "uncertain").lower(),
                "confidence": float(data.get("confidence", 0.5)),
                "reasoning": data.get("reasoning", "No reasoning provided"),
                "mutation_type": data.get("mutation_type"),
                "dissenting_opinions": data.get("dissenting_opinions", [])
            }
    except (json.JSONDecodeError, KeyError, ValueError):
        pass

    # Fallback
    verdict = "uncertain"
    if "faithful" in output.lower():
        verdict = "faithful"
    elif "mutation" in output.lower():
        verdict = "mutation"

    return {
        "verdict": verdict,
        "confidence": 0.5,
        "reasoning": output[:500] if output else "No reasoning",
        "mutation_type": None,
        "dissenting_opinions": []
    }


class FactCheckCrew:
    """
    CrewAI-based fact verification crew.

    Orchestrates a team of specialized fact-checking agents to analyze
    whether claims faithfully represent their source material.
    """

    def __init__(self, model: str = "gpt-4o-mini", mode: str = "one-shot"):
        """
        Initialize the fact-checking crew.

        Args:
            model: The LLM model to use
            mode: "one-shot" for parallel analysis, "deliberation" for sequential with discussion
        """
        self.model = model
        self.mode = mode

        # Create agents
        self.literalist = create_literalist_agent(model)
        self.contextualist = create_contextualist_agent(model)
        self.statistician = create_statistician_agent(model)
        self.judge = create_judge_agent(model)

    def _create_analysis_task(self, agent: Agent, claim: str, truth: str) -> Task:
        """Create an analysis task for an agent."""
        return Task(
            description=f"""Analyze whether the following CLAIM is a faithful representation of the SOURCE TRUTH, or if it's a mutation (distortion, exaggeration, missing context, etc.).

SOURCE TRUTH:
{truth}

CLAIM:
{claim}

Focus on your specific expertise. Be precise and cite specific differences or matches.""",
            expected_output="""A JSON object containing:
{
    "verdict": "faithful" | "mutation" | "uncertain",
    "confidence": <float 0.0-1.0>,
    "reasoning": "<your detailed reasoning>",
    "evidence": ["<specific evidence point 1>", "<specific evidence point 2>", ...]
}""",
            agent=agent,
        )

    def _create_synthesis_task(
        self,
        claim: str,
        truth: str,
        verdicts_context: str
    ) -> Task:
        """Create the final synthesis task for the judge."""
        return Task(
            description=f"""As Chief Judge, synthesize the following fact-checker opinions into a final verdict.

SOURCE TRUTH:
{truth}

CLAIM:
{claim}

FACT-CHECKER VERDICTS:
{verdicts_context}

Consider all perspectives and render a final verdict. Identify:
1. Points of agreement among fact-checkers
2. Key disagreements and how to resolve them
3. The most compelling evidence for your final verdict
4. If mutation, what type: temporal, numerical, contextual, or framing""",
            expected_output="""A JSON object containing:
{
    "verdict": "faithful" | "mutation" | "uncertain",
    "confidence": <float 0.0-1.0>,
    "reasoning": "<your synthesis and justification>",
    "mutation_type": "<temporal|numerical|contextual|framing|null>",
    "dissenting_opinions": ["<any significant dissenting views>"]
}""",
            agent=self.judge,
        )

    def run_debate(self, claim: str, truth: str, case_id: int = 0) -> CrewDebateResult:
        """
        Run the fact-checking debate on a claim.

        Args:
            claim: The claim to verify
            truth: The source truth
            case_id: Identifier for the case

        Returns:
            CrewDebateResult with all verdicts and final synthesis
        """
        # Phase 1: Create analysis tasks for each agent
        literalist_task = self._create_analysis_task(self.literalist, claim, truth)
        contextualist_task = self._create_analysis_task(self.contextualist, claim, truth)
        statistician_task = self._create_analysis_task(self.statistician, claim, truth)

        # Create crew for parallel analysis
        analysis_crew = Crew(
            agents=[self.literalist, self.contextualist, self.statistician],
            tasks=[literalist_task, contextualist_task, statistician_task],
            process=Process.sequential,  # Each agent works on their task
            verbose=False,
        )

        # Run analysis
        analysis_result = analysis_crew.kickoff()

        # Parse individual verdicts from task outputs
        initial_verdicts = []
        task_outputs = analysis_result.tasks_output if hasattr(analysis_result, 'tasks_output') else []

        agent_names = ["Literalist", "Contextualist", "Statistician"]
        for i, name in enumerate(agent_names):
            if i < len(task_outputs):
                output = str(task_outputs[i])
                verdict = parse_verdict_from_output(output, name)
            else:
                verdict = AgentVerdict(
                    agent_name=name,
                    verdict="uncertain",
                    confidence=0.0,
                    reasoning="No output received",
                    evidence=[]
                )
            initial_verdicts.append(verdict)

        # Phase 2: Synthesis - Judge reviews all opinions
        verdicts_context = "\n\n".join([
            f"**{v.agent_name}** ({v.verdict}, {v.confidence:.0%} confidence):\n{v.reasoning}"
            for v in initial_verdicts
        ])

        synthesis_task = self._create_synthesis_task(claim, truth, verdicts_context)

        synthesis_crew = Crew(
            agents=[self.judge],
            tasks=[synthesis_task],
            process=Process.sequential,
            verbose=False,
        )

        synthesis_result = synthesis_crew.kickoff()
        final = parse_final_verdict(str(synthesis_result))

        return CrewDebateResult(
            case_id=case_id,
            claim=claim,
            truth=truth,
            initial_verdicts=initial_verdicts,
            final_verdict=final["verdict"],
            final_confidence=final["confidence"],
            final_reasoning=final["reasoning"],
            mutation_type=final.get("mutation_type"),
            dissenting_opinions=final.get("dissenting_opinions", [])
        )


class SingleAgentCrewBaseline:
    """
    Single agent baseline using CrewAI for comparison.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.agent = Agent(
            role="Fact-Checker",
            goal="Determine if claims faithfully represent their source material",
            backstory="""You are an expert fact-checker analyzing whether claims faithfully represent their sources. You check for:
1. Factual accuracy (numbers, dates, specific details)
2. Context preservation (caveats, qualifiers, implications)
3. Statistical/numerical framing""",
            llm=LLM(model=model, api_key=OPENAI_API_KEY),
            verbose=False,
            allow_delegation=False,
        )

    def analyze(self, claim: str, truth: str, case_id: int = 0) -> CrewDebateResult:
        """Run single-agent analysis."""
        task = Task(
            description=f"""Analyze whether the following CLAIM is a faithful representation of the SOURCE TRUTH, or if it's a mutation.

SOURCE TRUTH:
{truth}

CLAIM:
{claim}

Consider factual accuracy, context preservation, and statistical framing.""",
            expected_output="""A JSON object:
{
    "verdict": "faithful" | "mutation" | "uncertain",
    "confidence": <float 0.0-1.0>,
    "reasoning": "<your detailed reasoning>",
    "evidence": ["<evidence point 1>", "<evidence point 2>"]
}""",
            agent=self.agent,
        )

        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
        )

        result = crew.kickoff()
        verdict = parse_verdict_from_output(str(result), "Single Agent")

        return CrewDebateResult(
            case_id=case_id,
            claim=claim,
            truth=truth,
            initial_verdicts=[verdict],
            final_verdict=verdict.verdict,
            final_confidence=verdict.confidence,
            final_reasoning=verdict.reasoning,
        )
