"""FastAPI server for FactTrace - Multi-Agent Fact Verification System."""

import asyncio
import csv
import json
from pathlib import Path
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MODELS, SETUPS
from agents import LiteralistAgent, ContextualistAgent, StatisticianAgent
from debate.protocol import DebateProtocol, DebateResult
from debate.verdict import VerdictSynthesizer
from debate.crew import FactCheckCrew


def load_cases():
    """Load all test cases from data.csv."""
    data_path = Path(__file__).parent.parent / "data.csv"
    cases = []

    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            claim = row['claim'].strip()
            truth = row['truth'].strip()

            # Generate a short name from the claim (first few words)
            words = claim.split()[:5]
            name = ' '.join(words)
            if len(claim.split()) > 5:
                name += '...'

            cases.append({
                "id": idx,
                "name": name,
                "mutation_type": "Unknown",
                "claim": claim,
                "truth": truth
            })

    return cases


CASES = load_cases()

AGENT_CLASSES = {
    "literalist": LiteralistAgent,
    "contextualist": ContextualistAgent,
    "statistician": StatisticianAgent,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("=" * 50)
    print("FactTrace API Server")
    print("=" * 50)
    print(f"Cases loaded: {len(CASES)}")
    print(f"Setups available: {list(SETUPS.keys())}")
    print(f"Models: {MODELS}")
    print("=" * 50)
    yield
    print("Shutting down...")


app = FastAPI(
    title="FactTrace API",
    description="Multi-Agent Fact Verification System - A jury of AI agents that debates truth",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Models ==============

class DebateRequest(BaseModel):
    case_id: int
    setup: str = "crew-jury"
    model: str = "mini"


class CaseResponse(BaseModel):
    id: int
    name: str
    mutation_type: str
    claim: str
    truth: str


# ============== Helpers ==============

def create_agents(agent_names: list[str], model: str) -> list:
    """Create agent instances."""
    return [AGENT_CLASSES[name](model=model) for name in agent_names]


async def run_agent_analysis(agent, claim: str, truth: str):
    """Run agent analysis in thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, agent.analyze, claim, truth)


async def run_agent_response(agent, verdicts, claim: str, truth: str):
    """Run agent response in thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, agent.respond_to, verdicts, claim, truth)


async def run_synthesis(synthesizer, debate_result):
    """Run verdict synthesis in thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, synthesizer.synthesize, debate_result)


# ============== SSE Streaming ==============

async def stream_debate(case: dict, setup_name: str, model_name: str) -> AsyncGenerator[str, None]:
    """Stream debate events as Server-Sent Events."""
    setup = SETUPS[setup_name]
    model = MODELS[model_name]
    paradigm = setup.get("paradigm", "baseline")

    def send_event(event_type: str, data) -> str:
        return f"data: {json.dumps({'type': event_type, 'data': data})}\n\n"

    # Send case info
    yield send_event('case', case)
    await asyncio.sleep(0.05)

    # Send setup info
    yield send_event('setup', {'name': setup_name, 'description': setup['description'], 'paradigm': paradigm})
    await asyncio.sleep(0.05)

    loop = asyncio.get_event_loop()

    # ============== PARADIGM: BASELINE (Single Agent) ==============
    if paradigm == "baseline":
        yield send_event('phase', 'Single Agent Analysis')
        yield send_event('status', 'Analyzing claim...')

        agent_info = [{"name": "Investigator", "color": "#9B8BC8", "role": "Comprehensive fact-checking"}]
        yield send_event('agents', agent_info)

        crew = FactCheckCrew(model=model, max_rounds=1)
        result = await loop.run_in_executor(
            None, crew.analyze, case["claim"], case["truth"], case["id"]
        )

        verdict = result.initial_verdicts[0]
        yield send_event('agent_verdict', {
            'agent_name': 'Investigator',
            'color': '#9B8BC8',
            'verdict': verdict.verdict,
            'confidence': verdict.confidence,
            'reasoning': verdict.reasoning,
            'evidence': verdict.evidence
        })

        yield send_event('final_verdict', {
            'verdict': result.final_verdict,
            'confidence': result.final_confidence,
            'reasoning': result.final_reasoning,
            'mutation_type': result.mutation_type
        })

    # ============== PARADIGM: ADVERSARIAL DEBATE ==============
    elif paradigm == "adversarial":
        agent_info = [
            {"name": "Proponent", "color": "#52c41a", "role": "Argues FOR faithfulness"},
            {"name": "Opponent", "color": "#ff4d4f", "role": "Argues AGAINST faithfulness"},
            {"name": "Judge", "color": "#5B4B8A", "role": "Neutral arbiter"},
        ]
        yield send_event('agents', agent_info)
        await asyncio.sleep(0.1)

        yield send_event('phase', 'Phase 1: Opening Arguments')
        yield send_event('agent_thinking', {'agent_name': 'Proponent', 'color': '#52c41a'})
        yield send_event('status', 'Proponent building case for faithfulness...')
        await asyncio.sleep(0.1)

        rounds = setup.get("rounds", 2)
        crew = FactCheckCrew(model=model, max_rounds=rounds)

        result = await loop.run_in_executor(
            None, crew.run_debate, case["claim"], case["truth"], case["id"]
        )

        # Stream the adversarial verdicts
        color_map = {"Proponent": "#52c41a", "Opponent": "#ff4d4f"}
        for verdict in result.initial_verdicts:
            yield send_event('agent_verdict', {
                'agent_name': verdict.agent_name,
                'color': color_map.get(verdict.agent_name, "#9B8BC8"),
                'verdict': verdict.verdict,
                'confidence': verdict.confidence,
                'reasoning': verdict.reasoning,
                'evidence': verdict.evidence
            })
            await asyncio.sleep(0.1)

        if result.debate_rounds:
            yield send_event('phase', 'Phase 2: Rebuttals')
            yield send_event('status', 'Agents exchanging rebuttals...')
            await asyncio.sleep(0.1)

        yield send_event('phase', 'Phase 3: Judge Deliberation')
        yield send_event('agent_thinking', {'agent_name': 'Judge', 'color': '#5B4B8A'})
        await asyncio.sleep(0.1)

        yield send_event('final_verdict', {
            'verdict': result.final_verdict,
            'confidence': result.final_confidence,
            'reasoning': result.final_reasoning,
            'mutation_type': result.mutation_type,
            'dissenting': result.dissenting_opinions
        })

    # ============== PARADIGM: JURY PANEL (6-Agent) ==============
    elif paradigm == "jury":
        agent_info = [
            {"name": "The Numerical Hawk", "color": "#1890ff", "role": "Numbers don't lie, but rounding can kill"},
            {"name": "The Temporal Detective", "color": "#52c41a", "role": "In a pandemic, yesterday's truth is today's lie"},
            {"name": "The Spirit Defender", "color": "#722ed1", "role": "Would a reasonable person be misled?"},
            {"name": "The Harm Assessor", "color": "#eb2f96", "role": "Facts shape behavior"},
            {"name": "The Devil's Advocate", "color": "#ff4d4f", "role": "ADVERSARIAL - stress-tests consensus"},
        ]
        yield send_event('agents', agent_info)
        await asyncio.sleep(0.1)

        yield send_event('phase', 'Phase 1: 6-Agent Tribunal Debate')

        crew = FactCheckCrew(model=model, max_rounds=10)

        # Show thinking for each juror
        for agent in agent_info:
            yield send_event('agent_thinking', {'agent_name': agent['name'], 'color': agent['color']})
            await asyncio.sleep(0.05)

        yield send_event('status', '5 agents debating until 80% consensus (max 10 rounds)...')

        result = await loop.run_in_executor(
            None, crew.run_debate, case["claim"], case["truth"], case["id"]
        )

        # Stream individual verdicts
        color_map = {
            "The Numerical Hawk": "#1890ff",
            "The Temporal Detective": "#52c41a",
            "The Spirit-of-the-Law Defender": "#722ed1",
            "The Harm Assessor": "#eb2f96",
            "The Devil's Advocate": "#ff4d4f",
        }
        for verdict in result.initial_verdicts:
            yield send_event('agent_verdict', {
                'agent_name': verdict.agent_name,
                'color': color_map.get(verdict.agent_name, "#9B8BC8"),
                'verdict': verdict.verdict,
                'confidence': verdict.confidence,
                'reasoning': verdict.reasoning,
                'evidence': verdict.evidence
            })
            await asyncio.sleep(0.1)

        actual_rounds = len(result.debate_rounds) if result.debate_rounds else 1
        yield send_event('phase', f'Synthesis Judge Verdict (after {actual_rounds} rounds)')
        yield send_event('final_verdict', {
            'verdict': result.final_verdict,
            'confidence': result.final_confidence,
            'reasoning': result.final_reasoning,
            'mutation_type': result.mutation_type,
            'dissenting': result.dissenting_opinions
        })

    # ============== PARADIGM: CRITIC-PROPOSER-JUDGE ==============
    elif paradigm == "critic-proposer":
        agent_info = [
            {"name": "Proposer", "color": "#1890ff", "role": "Initial assessment"},
            {"name": "Critic", "color": "#ff4d4f", "role": "Challenge & critique"},
            {"name": "Synthesizer", "color": "#faad14", "role": "Reconcile views"},
            {"name": "Judge", "color": "#5B4B8A", "role": "Final verdict"},
        ]
        yield send_event('agents', agent_info)
        await asyncio.sleep(0.1)

        yield send_event('phase', 'Step 1: Proposer Assessment')
        yield send_event('agent_thinking', {'agent_name': 'Proposer', 'color': '#1890ff'})
        yield send_event('status', 'Proposer generating initial interpretation...')

        crew = FactCheckCrew(model=model, max_rounds=3)

        result = await loop.run_in_executor(
            None, crew.run_debate, case["claim"], case["truth"], case["id"]
        )

        # Stream each step
        color_map = {"Proposer": "#1890ff", "Critic": "#ff4d4f", "Synthesizer": "#faad14"}
        step_names = ["Proposer Assessment", "Critic Challenge", "Synthesizer Reconciliation"]

        for i, verdict in enumerate(result.initial_verdicts):
            if i == 1:
                yield send_event('phase', 'Step 2: Critic Challenge')
                yield send_event('agent_thinking', {'agent_name': 'Critic', 'color': '#ff4d4f'})
            elif i == 2:
                yield send_event('phase', 'Step 3: Synthesizer Reconciliation')
                yield send_event('agent_thinking', {'agent_name': 'Synthesizer', 'color': '#faad14'})

            yield send_event('agent_verdict', {
                'agent_name': verdict.agent_name,
                'color': color_map.get(verdict.agent_name, "#9B8BC8"),
                'verdict': verdict.verdict,
                'confidence': verdict.confidence,
                'reasoning': verdict.reasoning,
                'evidence': verdict.evidence
            })
            await asyncio.sleep(0.1)

        yield send_event('phase', 'Step 4: Judge Final Verdict')
        yield send_event('agent_thinking', {'agent_name': 'Judge', 'color': '#5B4B8A'})
        await asyncio.sleep(0.1)

        yield send_event('final_verdict', {
            'verdict': result.final_verdict,
            'confidence': result.final_confidence,
            'reasoning': result.final_reasoning,
            'mutation_type': result.mutation_type,
            'dissenting': result.dissenting_opinions
        })

    # ============== PARADIGM: ITERATIVE DEBATE (6-Agent) ==============
    elif paradigm == "iterative":
        import queue
        import threading

        agent_info = [
            {"name": "The Numerical Hawk", "color": "#1890ff", "role": "Numbers don't lie, but rounding can kill"},
            {"name": "The Temporal Detective", "color": "#52c41a", "role": "In a pandemic, yesterday's truth is today's lie"},
            {"name": "The Spirit Defender", "color": "#722ed1", "role": "Would a reasonable person be misled?"},
            {"name": "The Harm Assessor", "color": "#eb2f96", "role": "Facts shape behavior"},
            {"name": "The Devil's Advocate", "color": "#ff4d4f", "role": "ADVERSARIAL - stress-tests consensus"},
        ]
        yield send_event('agents', agent_info)
        await asyncio.sleep(0.1)

        rounds = setup.get("rounds", 5)

        yield send_event('status', f'6-AGENT DEBATE: 3-{rounds} rounds until 80% consensus...')
        yield send_event('status', "Devil's Advocate will challenge any emerging consensus!")

        color_map = {
            "The Numerical Hawk": "#1890ff",
            "The Temporal Detective": "#52c41a",
            "The Spirit-of-the-Law Defender": "#722ed1",
            "The Harm Assessor": "#eb2f96",
            "The Devil's Advocate": "#ff4d4f",
        }

        # Use a queue to stream events from the background thread
        event_queue = queue.Queue()
        result_holder = [None]

        current_round = [1]

        def on_round_start(round_num):
            """Called when a new round starts."""
            if round_num == 1:
                event_queue.put(('phase', 'Round 1: Initial Positions'))
            else:
                event_queue.put(('phase', f'Round {round_num}: Rebuttals'))
            event_queue.put(('debate_round', round_num))

        def on_agent_thinking(agent_name):
            """Called when an agent starts thinking."""
            event_queue.put(('agent_thinking', {
                'agent_name': agent_name,
                'color': color_map.get(agent_name, "#9B8BC8")
            }))

        def on_verdict(verdict):
            """Called when each agent submits a verdict."""
            event_queue.put(('agent_verdict', {
                'agent_name': verdict.agent_name,
                'color': color_map.get(verdict.agent_name, "#9B8BC8"),
                'verdict': verdict.verdict,
                'confidence': verdict.confidence,
                'reasoning': verdict.reasoning,
                'evidence': verdict.evidence
            }))

        def on_round_complete(round_num, verdicts):
            """Called when a round completes."""
            event_queue.put(('round_complete', round_num))

        def run_debate():
            crew = FactCheckCrew(model=model, max_rounds=rounds)
            result_holder[0] = crew.run_debate(
                case["claim"], case["truth"], case["id"],
                on_verdict=on_verdict,
                on_round_complete=on_round_complete,
                on_agent_thinking=on_agent_thinking,
                on_round_start=on_round_start
            )
            event_queue.put(('done', None))

        # Start debate in background thread
        debate_thread = threading.Thread(target=run_debate)
        debate_thread.start()

        # Stream events as they come in
        while True:
            try:
                event_type, event_data = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: event_queue.get(timeout=0.5)
                )

                if event_type == 'done':
                    break
                elif event_type == 'debate_round':
                    yield send_event('debate_round', event_data)
                elif event_type == 'agent_thinking':
                    yield send_event('agent_thinking', event_data)
                elif event_type == 'agent_verdict':
                    yield send_event('agent_verdict', event_data)
                elif event_type == 'round_complete':
                    yield send_event('status', f'Round {event_data} complete')
                elif event_type == 'phase':
                    yield send_event('phase', event_data)

                await asyncio.sleep(0.05)
            except:
                # Queue timeout - check if thread is still alive
                if not debate_thread.is_alive():
                    break

        debate_thread.join()
        result = result_holder[0]

        actual_rounds = len(result.debate_rounds) if result.debate_rounds else 1
        if actual_rounds < rounds:
            yield send_event('status', f'Consensus reached after {actual_rounds} round(s)')
        else:
            yield send_event('status', f'Max rounds reached - taking majority vote')

        yield send_event('phase', 'Synthesis Judge Deliberation')
        yield send_event('agent_thinking', {'agent_name': 'The Synthesis Judge', 'color': '#faad14'})
        await asyncio.sleep(0.1)

        yield send_event('final_verdict', {
            'verdict': result.final_verdict,
            'confidence': result.final_confidence,
            'reasoning': result.final_reasoning,
            'mutation_type': result.mutation_type,
            'dissenting': result.dissenting_opinions
        })

    # ============== LEGACY: Non-CrewAI paths ==============
    elif setup.get("mode") == "single":
        # Original single agent baseline
        yield send_event('phase', 'Single Agent Analysis')
        yield send_event('status', 'Analyzing claim...')

        from debate.protocol import SingleAgentBaseline
        baseline = SingleAgentBaseline(model=model)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, baseline.analyze, case["claim"], case["truth"], case["id"]
        )

        verdict = result.initial_verdicts[0]
        yield send_event('agent_verdict', {
            'agent_name': 'Single Agent',
            'color': 'gold',
            'verdict': verdict.verdict,
            'confidence': verdict.confidence,
            'reasoning': verdict.reasoning,
            'evidence': verdict.evidence
        })

        yield send_event('final_verdict', {
            'verdict': verdict.verdict,
            'confidence': verdict.confidence,
            'reasoning': verdict.reasoning,
            'mutation_type': None
        })

    else:
        # Original multi-agent jury
        agents = create_agents(setup["agents"], model)

        # Send agent intro
        agent_info = [{"name": a.name, "color": a.color, "role": a.role_description} for a in agents]
        yield send_event('agents', agent_info)
        await asyncio.sleep(0.1)

        # Phase 1: Independent Analysis
        yield send_event('phase', 'Phase 1: Independent Analysis')
        await asyncio.sleep(0.1)

        verdicts = []
        for agent in agents:
            yield send_event('agent_thinking', {'agent_name': agent.name, 'color': agent.color})

            verdict = await run_agent_analysis(agent, case["claim"], case["truth"])
            verdicts.append(verdict)

            yield send_event('agent_verdict', {
                'agent_name': verdict.agent_name,
                'color': agent.color,
                'verdict': verdict.verdict,
                'confidence': verdict.confidence,
                'reasoning': verdict.reasoning,
                'evidence': verdict.evidence
            })
            await asyncio.sleep(0.1)

        # Phase 2: Deliberation (if enabled)
        if setup["mode"] == "deliberation" and setup.get("rounds", 0) > 0:
            yield send_event('phase', 'Phase 2: Deliberation')
            await asyncio.sleep(0.1)

            for round_num in range(1, setup.get("rounds", 1) + 1):
                yield send_event('debate_round', round_num)

                for agent in agents:
                    yield send_event('agent_thinking', {'agent_name': agent.name, 'color': agent.color})

                    response = await run_agent_response(agent, verdicts, case["claim"], case["truth"])

                    yield send_event('agent_response', {
                        'agent_name': agent.name,
                        'color': agent.color,
                        'response': response
                    })
                    await asyncio.sleep(0.1)

        # Phase 3: Synthesis
        yield send_event('phase', 'Phase 3: Verdict Synthesis')
        yield send_event('status', 'Judge synthesizing final verdict...')
        await asyncio.sleep(0.1)

        debate_result = DebateResult(
            case_id=case["id"],
            claim=case["claim"],
            truth=case["truth"],
            initial_verdicts=verdicts,
            debate_rounds=[]
        )

        synthesizer = VerdictSynthesizer(strategy=setup["synthesis"], model=model)
        final = await run_synthesis(synthesizer, debate_result)

        yield send_event('final_verdict', {
            'verdict': final.verdict,
            'confidence': final.confidence,
            'reasoning': final.reasoning,
            'mutation_type': final.mutation_type,
            'dissenting': final.dissenting_opinions
        })

    yield send_event('done', None)


# ============== API Endpoints ==============

@app.get("/")
async def root():
    """Health check and API info."""
    return {
        "name": "FactTrace API",
        "version": "1.0.0",
        "description": "Multi-Agent Fact Verification System",
        "endpoints": {
            "cases": "/api/cases",
            "setups": "/api/setups",
            "debate_stream": "/api/debate/stream?case_id=1&setup=jury-llm&model=mini"
        }
    }


@app.get("/api/cases")
async def get_cases():
    """Get all available test cases."""
    return {"cases": CASES, "count": len(CASES)}


@app.get("/api/cases/{case_id}")
async def get_case(case_id: int):
    """Get a specific case by ID."""
    case = next((c for c in CASES if c["id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return case


@app.get("/api/setups")
async def get_setups():
    """Get all available debate setups."""
    return {
        "setups": {k: {"name": k, **v} for k, v in SETUPS.items()},
        "default": "crew-jury"
    }


@app.get("/api/models")
async def get_models():
    """Get available models."""
    return {"models": MODELS, "default": "mini"}


@app.get("/api/debate/stream")
async def stream_debate_endpoint(
    case_id: int,
    setup: str = "jury-llm",
    model: str = "mini"
):
    """
    Stream a debate as Server-Sent Events.

    Watch the jury deliberate in real-time!
    """
    # Validate case
    case = next((c for c in CASES if c["id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    # Validate setup
    if setup not in SETUPS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid setup '{setup}'. Available: {list(SETUPS.keys())}"
        )

    # Validate model
    if model not in MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model '{model}'. Available: {list(MODELS.keys())}"
        )

    return StreamingResponse(
        stream_debate(case, setup, model),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ============== Run Server ==============

def main():
    """Run the server."""
    import uvicorn
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(Path(__file__).parent.parent)]
    )


if __name__ == "__main__":
    main()
