"""FastAPI server for FactTrace - Multi-Agent Fact Verification System."""

import asyncio
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
from debate.crew import FactCheckCrew, SingleAgentCrewBaseline


def load_cases():
    """Load cases from JSON file."""
    data_path = Path(__file__).parent.parent / "data" / "cases.json"
    with open(data_path) as f:
        return json.load(f)["cases"]


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
    use_crewai = setup.get("use_crewai", False)

    def send_event(event_type: str, data) -> str:
        return f"data: {json.dumps({'type': event_type, 'data': data})}\n\n"

    # Send case info
    yield send_event('case', case)
    await asyncio.sleep(0.05)

    # Send setup info
    yield send_event('setup', {'name': setup_name, 'description': setup['description']})
    await asyncio.sleep(0.05)

    if use_crewai:
        # CrewAI-based execution
        if setup["mode"] == "single":
            yield send_event('phase', 'CrewAI Single Agent Analysis')
            yield send_event('status', 'Analyzing claim with CrewAI...')

            crew_baseline = SingleAgentCrewBaseline(model=model)

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, crew_baseline.analyze, case["claim"], case["truth"], case["id"]
            )

            verdict = result.initial_verdicts[0]
            yield send_event('agent_verdict', {
                'agent_name': 'CrewAI Agent',
                'color': 'gold',
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
        else:
            # CrewAI multi-agent jury
            agent_info = [
                {"name": "Literalist", "color": "red", "role": "Verify exact factual accuracy"},
                {"name": "Contextualist", "color": "blue", "role": "Examine context preservation"},
                {"name": "Statistician", "color": "green", "role": "Analyze numerical claims"},
                {"name": "Judge", "color": "purple", "role": "Synthesize final verdict"},
            ]
            yield send_event('agents', agent_info)
            await asyncio.sleep(0.1)

            yield send_event('phase', 'CrewAI Jury Analysis')
            yield send_event('status', 'CrewAI agents deliberating...')

            crew = FactCheckCrew(model=model, mode=setup["mode"])

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, crew.run_debate, case["claim"], case["truth"], case["id"]
            )

            # Stream individual verdicts
            color_map = {"Literalist": "red", "Contextualist": "blue", "Statistician": "green"}
            for verdict in result.initial_verdicts:
                yield send_event('agent_verdict', {
                    'agent_name': verdict.agent_name,
                    'color': color_map.get(verdict.agent_name, "white"),
                    'verdict': verdict.verdict,
                    'confidence': verdict.confidence,
                    'reasoning': verdict.reasoning,
                    'evidence': verdict.evidence
                })
                await asyncio.sleep(0.1)

            yield send_event('phase', 'Judge Synthesis')
            yield send_event('final_verdict', {
                'verdict': result.final_verdict,
                'confidence': result.final_confidence,
                'reasoning': result.final_reasoning,
                'mutation_type': result.mutation_type,
                'dissenting': result.dissenting_opinions
            })

    elif setup["mode"] == "single":
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
