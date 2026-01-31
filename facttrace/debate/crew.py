"""CrewAI-based 6-agent debate for fact verification.

Implements the 6-agent jury panel debate:
1. The Numerical Hawk - Obsesses over quantitative precision
2. The Temporal Detective - Specializes in time-related distortions
3. The Spirit-of-the-Law Defender - Argues for contextual/practical equivalence
4. The Harm Assessor - Evaluates real-world consequences of mutations
5. The Devil's Advocate - Stress-tests the emerging consensus
6. The Synthesis Judge - Summarizes and forces final verdict
"""

import json
import re
from typing import Optional, Callable
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


# ============== Agent Factory Functions ==============

def create_numerical_hawk_agent(model: str) -> Agent:
    """The Numerical Hawk - Obsesses over quantitative precision."""
    return Agent(
        role="The Numerical Hawk",
        goal="FLAG ANY NUMERICAL DISCREPANCY. Be pedantic and uncompromising on numbers.",
        backstory="""You are THE NUMERICAL HAWK, OBSESSED with quantitative precision.

YOUR PERSONALITY: Pedantic, uncompromising on numbers.

YOU FLAG ANY NUMERICAL DISCREPANCY:
- 375,000 vs 374,000 - THAT'S 1,000 PEOPLE!
- In a pandemic, "off by 1,000 cases" could affect policy decisions
- You will die on the hill of "87 ≠ 70"
- Percentages matter: 2.5% vs 3% is a significant difference

YOUR DETECTION TOOLKIT:
- "The source says 374,000 but the claim says 375,000 - THAT'S A 1,000 DIFFERENCE!"
- "87 is NOT the same as 'more than 70' - precision matters!"
- "This number was INFLATED/DEFLATED by X%"

YOU ARE PEDANTIC ABOUT:
- Exact figures vs rounded figures
- "More than" vs "less than" vs "exactly" vs "approximately"
- Order of magnitude accuracy

CATCHPHRASE: "Numbers don't lie, but rounding can kill."

Be confrontational about numerical errors. Small errors compound into big lies.""",
        llm=LLM(model=model, api_key=OPENAI_API_KEY),
        verbose=False,
        allow_delegation=False,
    )


def create_temporal_detective_agent(model: str) -> Agent:
    """The Temporal Detective - Specializes in time-related distortions."""
    return Agent(
        role="The Temporal Detective",
        goal="CATCH EVERY TEMPORAL SHIFT. Specialize in time-related distortions.",
        backstory="""You are THE TEMPORAL DETECTIVE, specializing in time-related distortions.

YOUR PERSONALITY: Sharp, suspicious of date shifts.

YOU OBSESS OVER:
- "as of" vs "after" vs "by" vs "before" - THESE ARE DIFFERENT!
- COVID data changed DAILY—one day matters!
- "As of February 13" ≠ "After February 13" - completely different meanings!
- Date shifts that seem minor but change the data entirely

YOUR DETECTION TOOLKIT:
- "AS OF ≠ AFTER ≠ BY ≠ BEFORE - these are DIFFERENT temporal operators!"
- "The source says March 23, the claim says March 24 - that's a DAY SHIFT!"
- "The claim says 'after February 13' but the source says 'as of February 13'—completely different meaning!"

YOU ARE PEDANTIC ABOUT:
- "As of" (snapshot at time T) vs "after" (subsequent to time T)
- "Before" vs "by" vs "until" vs "as of"
- Date precision in fast-moving situations

CATCHPHRASE: "In a pandemic, yesterday's truth is today's lie."

Time is sacred. Call out EVERY temporal shift.""",
        llm=LLM(model=model, api_key=OPENAI_API_KEY),
        verbose=False,
        allow_delegation=False,
    )


def create_spirit_defender_agent(model: str) -> Agent:
    """The Spirit-of-the-Law Defender - Argues for contextual/practical equivalence."""
    return Agent(
        role="The Spirit-of-the-Law Defender",
        goal="Argue for contextual and practical equivalence. Defend claims that are directionally correct.",
        backstory="""You are THE SPIRIT-OF-THE-LAW DEFENDER, arguing for contextual/practical equivalence.

YOUR PERSONALITY: Pragmatic, patient, slightly frustrated by pedants.

YOUR CORE ARGUMENT:
- "Close enough" if the takeaway message is preserved
- Defend claims that are directionally correct
- Focus on whether the ESSENTIAL meaning is preserved
- Argue that minor discrepancies don't mislead reasonable readers

YOUR DEFENSE TOOLKIT:
- "Yes, it was 87 cases not 70—but the claim said 'more than 70' which is TECHNICALLY TRUE."
- "Both convey 'roughly 375k by late March.' No one is misled."
- "The spirit of the claim is preserved even if the letter isn't."
- "You're being TOO pedantic—real-world communication allows for this!"

YOUR STANDARDS:
- Would a reasonable person be misled?
- Is the core message preserved?
- Is the claim directionally correct?

CATCHPHRASE: "Would a reasonable person be misled? That's the only question."

Push back against excessive pedantry while maintaining honesty.""",
        llm=LLM(model=model, api_key=OPENAI_API_KEY),
        verbose=False,
        allow_delegation=False,
    )


def create_harm_assessor_agent(model: str) -> Agent:
    """The Harm Assessor - Evaluates real-world consequences of mutations."""
    return Agent(
        role="The Harm Assessor",
        goal="Evaluate real-world consequences of factual mutations. Focus on potential harm.",
        backstory="""You are THE HARM ASSESSOR, evaluating real-world consequences of mutations.

YOUR PERSONALITY: Serious, outcome-focused, ethically driven.

YOUR CORE QUESTION:
"Would this mutation cause someone to act differently?"

YOUR ASSESSMENT FRAMEWORK:
- Understating deaths = dangerous complacency
- Overstating cases = unnecessary panic
- Shifting dates = wrong policy timing
- Missing context = flawed decision-making

YOU CONSIDER:
- Public health impact of the mutation
- Could this cause harmful behavior changes?
- Does the error create false urgency or false comfort?
- Would policymakers or the public act differently based on the mutated claim?

YOUR ANALYSIS APPROACH:
- "This slight inflation + date shift could create false urgency—but the error is <1%. Low harm."
- "Understating by 10,000 deaths could lead to premature reopening. HIGH HARM."
- "The directional message is correct; impact on behavior is minimal."

YOU BREAK TIES based on potential real-world impact.

CATCHPHRASE: "Facts don't exist in a vacuum—they shape behavior."

Be the ethical compass. Evaluate consequences, not just accuracy.""",
        llm=LLM(model=model, api_key=OPENAI_API_KEY),
        verbose=False,
        allow_delegation=False,
    )


def create_devils_advocate_agent(model: str) -> Agent:
    """The Devil's Advocate - Stress-tests the emerging consensus."""
    return Agent(
        role="The Devil's Advocate",
        goal="STRESS-TEST THE EMERGING CONSENSUS. Prevent groupthink. Be productively contrarian.",
        backstory="""You are THE DEVIL'S ADVOCATE, here to stress-test the emerging consensus.

YOUR PERSONALITY: Contrarian, sharp, enjoys chaos (productively).

YOUR PRIME DIRECTIVE: CHALLENGE THE CONSENSUS

YOUR ROLE:
- If the group leans "Faithful," argue for "Mutation"
- If the group leans "Mutation," argue for "Faithful"
- Force the jury to articulate WHY they believe what they believe
- Prevent groupthink at all costs

YOUR WEAPONS:
- "You're all agreeing too fast. What are you missing?"
- "But wait—if we let 'close enough' slide here, where do we draw the line?"
- "Actually, consider the opposite interpretation..."
- "Everyone's focused on X, but what about Y?"

YOUR PURPOSE:
- Expose weak reasoning
- Force others to defend their positions
- Find the blind spots in the majority view
- Ensure no conclusion is reached without rigorous challenge

CATCHPHRASE: "You're all agreeing too fast. What are you missing?"

Be provocative. Be challenging. Make this a REAL debate.""",
        llm=LLM(model=model, api_key=OPENAI_API_KEY),
        verbose=False,
        allow_delegation=False,
    )


def create_synthesis_judge_agent(model: str) -> Agent:
    """The Synthesis Judge - Summarizes and forces final verdict, grounded in cybernetics and epistemic pluralism."""
    return Agent(
        role="The Synthesis Judge",
        goal="Synthesize all positions through cybernetic feedback and epistemic pluralism to render the final verdict.",
        backstory="""You are THE SYNTHESIS JUDGE, a philosophical arbiter grounded in CYBERNETICS and EPISTEMIC PLURALISM.

YOUR PHILOSOPHICAL FRAMEWORK:

CYBERNETICS - You view this debate as a self-regulating system:
- Each agent's perspective is a FEEDBACK LOOP that corrects and refines understanding
- Disagreement is not noise—it's SIGNAL that reveals blind spots in the system
- Truth emerges through iterative cycles of claim, counter-claim, and synthesis
- The system's intelligence exceeds any single agent's knowledge

EPISTEMIC PLURALISM - You honor multiple valid ways of knowing:
- The Numerical Hawk's precision-based epistemology (quantitative truth)
- The Temporal Detective's temporal epistemology (truth is time-bound)
- The Spirit Defender's pragmatic epistemology (truth serves understanding)
- The Harm Assessor's consequentialist epistemology (truth shapes action)
- The Devil's Advocate's dialectical epistemology (truth emerges from opposition)

YOUR SYNTHESIS PROCESS:
1. MAP THE EPISTEMIC LANDSCAPE: What does each way of knowing reveal?
2. IDENTIFY FEEDBACK LOOPS: Where do perspectives reinforce or correct each other?
3. FIND CONVERGENCE: What truth claims survive multiple epistemic lenses?
4. HONOR DIVERGENCE: What legitimate dissent must be preserved?
5. RENDER JUDGMENT: Synthesize into actionable verdict

YOUR VERDICT MUST:
- Acknowledge that truth is multi-dimensional, not singular
- Explain how different epistemic approaches informed the conclusion
- Note where feedback loops between agents strengthened or weakened claims
- Preserve dissenting views as valuable minority reports
- Ground the final verdict in the CONVERGENCE of multiple ways of knowing

CATCHPHRASE: "Truth is not found in any single perspective, but in the cybernetic dance between them."

Your verdict reflects not just accuracy, but WISDOM—the integration of multiple valid epistemologies.""",
        llm=LLM(model=model, api_key=OPENAI_API_KEY),
        verbose=False,
        allow_delegation=False,
    )


# ============== Parsing Utilities ==============

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


# ============== 6-AGENT DEBATE CREW ==============

class FactCheckCrew:
    """
    6-Agent Debate Crew for Fact Verification.

    Debate Flow:
    - Minimum 3 rounds, maximum 5 rounds
    - Each round: All 5 debaters see previous positions and respond
    - Consensus (80%+ agreement) can stop debate after round 3
    - If no consensus after max rounds, take majority vote
    - Synthesis Judge renders final verdict with reasoning

    Agents:
    1. The Numerical Hawk - Obsesses over quantitative precision
    2. The Temporal Detective - Specializes in time-related distortions
    3. The Spirit-of-the-Law Defender - Argues for contextual/practical equivalence
    4. The Harm Assessor - Evaluates real-world consequences of mutations
    5. The Devil's Advocate - Stress-tests the emerging consensus
    6. The Synthesis Judge - Summarizes and forces final verdict
    """

    def __init__(self, model: str = "gpt-4o-mini", max_rounds: int = 5):
        self.model = model
        self.max_rounds = max_rounds

        # Create all 6 specialized agents
        self.numerical_hawk = create_numerical_hawk_agent(model)
        self.temporal_detective = create_temporal_detective_agent(model)
        self.spirit_defender = create_spirit_defender_agent(model)
        self.harm_assessor = create_harm_assessor_agent(model)
        self.devils_advocate = create_devils_advocate_agent(model)
        self.judge = create_synthesis_judge_agent(model)

        # Debating agents (excludes the judge who synthesizes at the end)
        self.agents = [
            ("The Numerical Hawk", self.numerical_hawk),
            ("The Temporal Detective", self.temporal_detective),
            ("The Spirit-of-the-Law Defender", self.spirit_defender),
            ("The Harm Assessor", self.harm_assessor),
            ("The Devil's Advocate", self.devils_advocate),
        ]

    def _check_consensus(self, verdicts: list[AgentVerdict], threshold: float = 0.8) -> bool:
        """Check if agents have reached consensus (80%+ same verdict)."""
        vote_counts = {}
        for v in verdicts:
            vote_counts[v.verdict] = vote_counts.get(v.verdict, 0) + 1

        total = len(verdicts)
        for count in vote_counts.values():
            if count / total >= threshold:
                return True
        return False

    def _get_majority_verdict(self, verdicts: list[AgentVerdict]) -> str:
        """Get the majority verdict from the agents."""
        vote_counts = {}
        for v in verdicts:
            vote_counts[v.verdict] = vote_counts.get(v.verdict, 0) + 1
        return max(vote_counts, key=vote_counts.get)

    def run_debate(
        self,
        claim: str,
        truth: str,
        case_id: int = 0,
        on_verdict: Optional[Callable] = None,
        on_round_complete: Optional[Callable] = None,
        on_agent_thinking: Optional[Callable] = None,
        on_round_start: Optional[Callable] = None,
    ) -> CrewDebateResult:
        """Run the 6-agent debate."""
        all_verdicts = []
        debate_rounds = []
        current_context = ""

        for round_num in range(1, self.max_rounds + 1):
            # Notify round start
            if on_round_start:
                on_round_start(round_num)

            round_verdicts = []
            round_context = f"\n=== Round {round_num} ===\n"

            for name, agent in self.agents:
                # Notify that agent is thinking
                if on_agent_thinking:
                    on_agent_thinking(name)
                if round_num == 1:
                    # Round 1: Independent initial positions
                    task_desc = f"""Analyze whether this CLAIM faithfully represents the SOURCE.

SOURCE TRUTH:
{truth}

CLAIM:
{claim}

Provide your INDEPENDENT assessment. Focus on your area of expertise."""
                else:
                    # Subsequent rounds: See others' positions and respond
                    task_desc = f"""Continue the investigation. Review your colleagues' assessments:

{current_context}

SOURCE TRUTH:
{truth}

CLAIM:
{claim}

Consider their arguments. Respond to points you agree or disagree with.
Have they raised valid concerns you missed? Do you want to update your assessment?"""

                task = Task(
                    description=task_desc,
                    expected_output="""A JSON object:
{
    "verdict": "faithful" | "mutation" | "uncertain",
    "confidence": <float 0.0-1.0>,
    "reasoning": "<your reasoning>",
    "evidence": ["<point 1>", "<point 2>", ...]
}""",
                    agent=agent,
                )

                crew = Crew(
                    agents=[agent],
                    tasks=[task],
                    process=Process.sequential,
                    verbose=False,
                )
                result = crew.kickoff()
                output = str(result)
                verdict = parse_verdict_from_output(output, name)
                round_verdicts.append(verdict)
                round_context += f"\n{name}: {verdict.verdict} ({verdict.confidence:.0%}) - {verdict.reasoning[:300]}...\n"

                if on_verdict:
                    on_verdict(verdict)

            all_verdicts = round_verdicts
            debate_rounds.append({
                "round": round_num,
                "verdicts": [(v.agent_name, v.verdict, v.confidence, v.reasoning) for v in round_verdicts]
            })
            current_context += round_context

            if on_round_complete:
                on_round_complete(round_num, round_verdicts)

            # Check for consensus (80%+ agreement) - stop early, but only after minimum 3 rounds
            if round_num >= 3 and self._check_consensus(round_verdicts):
                break

        # Determine consensus status and majority verdict
        reached_consensus = self._check_consensus(all_verdicts)
        majority_verdict = self._get_majority_verdict(all_verdicts)

        # Final synthesis by judge
        verdicts_summary = "\n\n".join([
            f"**{v.agent_name}** votes '{v.verdict}' ({v.confidence:.0%} confidence):\n{v.reasoning}"
            for v in all_verdicts
        ])

        consensus_status = "CONSENSUS REACHED" if reached_consensus else f"NO CONSENSUS after {self.max_rounds} rounds - MAJORITY VOTE: {majority_verdict}"

        judge_task = Task(
            description=f"""After {len(debate_rounds)} round(s) of cybernetic deliberation, synthesize the final verdict through epistemic pluralism.

STATUS: {consensus_status}

SOURCE TRUTH:
{truth}

CLAIM:
{claim}

FINAL POSITIONS (Each represents a distinct epistemic lens):
{verdicts_summary}

DEBATE HISTORY:
{current_context}

Apply your CYBERNETIC and EPISTEMIC PLURALIST framework:

1. MAP THE EPISTEMIC LANDSCAPE: What truth does each agent's way of knowing reveal?
   - Numerical Hawk: Quantitative precision epistemology
   - Temporal Detective: Time-bound truth epistemology
   - Spirit Defender: Pragmatic/contextual epistemology
   - Harm Assessor: Consequentialist epistemology
   - Devil's Advocate: Dialectical epistemology

2. TRACE THE FEEDBACK LOOPS: How did agents' positions evolve through debate? What corrections emerged?

3. FIND CONVERGENCE: What claims survived scrutiny from MULTIPLE epistemic approaches?

4. HONOR DIVERGENCE: What legitimate minority views must be preserved as valuable dissent?

5. SYNTHESIZE: Ground your verdict in the CONVERGENCE of multiple ways of knowing, not just majority vote.

{"The agents reached consensus - explain what epistemic convergence produced this agreement." if reached_consensus else "The majority voted '" + majority_verdict + "' - synthesize why multiple epistemic lenses point to this conclusion, or explain your disagreement."}

Remember: Truth emerges from the cybernetic dance between perspectives, not from any single viewpoint.""",
            expected_output="""A JSON object:
{
    "verdict": "faithful" | "mutation",
    "confidence": <float 0.0-1.0>,
    "reasoning": "<Your synthesis grounded in cybernetics and epistemic pluralism - explain how different ways of knowing converged or diverged, and what the feedback loops revealed>",
    "mutation_type": "<temporal|numerical|contextual|framing|null>",
    "dissenting_opinions": ["<valuable minority epistemology that deserves preservation>", ...]
}""",
            agent=self.judge,
        )

        judge_crew = Crew(
            agents=[self.judge],
            tasks=[judge_task],
            process=Process.sequential,
            verbose=False,
        )
        judge_result = judge_crew.kickoff()
        final = parse_final_verdict(str(judge_result))

        return CrewDebateResult(
            case_id=case_id,
            claim=claim,
            truth=truth,
            initial_verdicts=all_verdicts,
            debate_rounds=debate_rounds,
            final_verdict=final["verdict"],
            final_confidence=final["confidence"],
            final_reasoning=final["reasoning"],
            mutation_type=final.get("mutation_type"),
            dissenting_opinions=final.get("dissenting_opinions", [])
        )
