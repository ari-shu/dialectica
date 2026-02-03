# Dialectica

A multi-agent fact verification system that uses a "jury of AI agents" to debate whether claims are faithful representations of source facts or mutations.

Built for the Cambridge FactTrace Hackathon.

## Overview

FactTrace addresses the challenge of detecting subtle misinformation. Instead of a single AI making a binary decision, we use multiple specialized agents that analyze claims from different perspectives and debate to reach a consensus verdict.

### The Problem

Given a **source truth** and an **external claim**, determine if the claim is:
- **Faithful**: Accurately represents the source
- **Mutation**: Distorts the source through exaggeration, missing context, numerical manipulation, etc.

### Our Approach

Three specialized AI agents form a jury, each with a distinct methodology:

---

#### 🔴 Literalist

**Role**: Pedantic Fact-Checker

**Methodology**: The Literalist performs strict textual comparison between the claim and source. It treats any deviation in hard facts as a potential mutation.

**What it checks**:
- Exact numbers, dates, and quantities
- Precise wording and terminology
- Temporal markers ("as of" vs "after" vs "by")
- Direct contradictions

**Standards**:
- Numbers must match exactly or rounding must be clearly justified
- Dates and timeframes must be precisely preserved
- "More than X" ≠ "exactly X" ≠ "X"

**Example trigger**: Source says "as of Feb 13" but claim says "after Feb 13" → Mutation (temporal shift)

---

#### 🔵 Contextualist

**Role**: Context Preservation Analyzer

**Methodology**: The Contextualist evaluates whether the claim preserves the spirit and implications of the source, not just the letter. A fact without its caveat can be misleading even if technically accurate.

**What it checks**:
- Omitted caveats and qualifiers
- Missing uncertainty language
- Cherry-picked facts that misrepresent the whole
- Shifted implications or tone

**Standards**:
- Important context must be preserved
- Uncertainty in the source should be reflected
- Geographic/demographic scope must match
- Reader should get the same impression from claim as from source

**Example trigger**: Source says "official figures may not have counted..." but claim omits this → Mutation (missing caveat)

---

#### 🟢 Statistician

**Role**: Numerical Framing Expert

**Methodology**: The Statistician analyzes how numbers are presented and whether the framing is fair. It balances pedantry with practicality—minor rounding may be acceptable, but date shifts to inflate numbers are not.

**What it checks**:
- Rounding accuracy and appropriateness
- Date/time shifts in data attribution
- Numerical understatements or overstatements
- Misleading statistical framing

**Standards**:
- Rounding should not materially change meaning
- Data should be attributed to correct dates
- Numerical precision should match source
- Comparisons should be fair

**Example trigger**: Source says "374,000 as of March 23" but claim says "375,000 by March 24" → Mutation (date shift + rounding)

---

Each agent independently analyzes the claim, then a synthesis step (majority vote or LLM judge) produces a final verdict.

## Features

- **Live Debate Visualization**: Watch agents analyze and deliberate in real-time via streaming UI
- **Multiple Setups**: Compare single-agent baseline vs multi-agent jury
- **Configurable Synthesis**: Majority vote or LLM-based verdict synthesis
- **Deliberation Mode**: Optional round where agents respond to each other's verdicts

## Project Structure

```
facttrace/
├── api/
│   └── server.py           # FastAPI backend with SSE streaming
├── ui/                     # React + Ant Design frontend
│   └── src/
│       ├── App.tsx
│       ├── App.css
│       └── components/
│           ├── CaseSelector.tsx
│           ├── AgentCard.tsx
│           ├── VerdictCard.tsx
│           └── DebateTimeline.tsx
├── agents/
│   ├── base_agent.py       # Abstract agent with LLM calls
│   ├── literalist.py       # Exact accuracy checker
│   ├── contextualist.py    # Context preservation checker
│   └── statistician.py     # Numerical framing checker
├── debate/
│   ├── protocol.py         # Debate orchestration
│   └── verdict.py          # Verdict synthesis (majority/LLM)
├── utils/
│   └── display.py          # CLI pretty printing (rich)
├── data/
│   └── cases.json          # 5 test cases
├── main.py                 # CLI entry point
├── config.py               # Model & setup configuration
├── requirements.txt
├── run.sh                  # Start backend + frontend
└── run-api.sh              # Start backend only
```

## Setup

### 1. Install Dependencies

```bash
cd facttrace

# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd ui && npm install && cd ..
```

### 2. Configure API Key

```bash
echo "OPENAI_API_KEY=your-key-here" > .env
```

### 3. Run

**Option A: Full UI (recommended for demo)**

Terminal 1 - Backend:
```bash
cd facttrace
python -m uvicorn api.server:app --reload --port 8000
```

Terminal 2 - Frontend:
```bash
cd facttrace/ui
npm run dev
```

Then open http://localhost:5173

**Option B: CLI only**

```bash
python main.py --case 1
```

## Available Setups

| Setup | Description |
|-------|-------------|
| `single` | Single agent baseline (no jury) |
| `jury-vote` | 3 agents with confidence-weighted majority vote |
| `jury-llm` | 3 agents with LLM judge synthesis (default) |
| `jury-deliberate` | 3 agents + deliberation round + LLM synthesis |

## Test Cases

| Case | Name | Mutation Type | Description |
|------|------|---------------|-------------|
| 1 | Maxthon Browser | Framing Flip | Removes geographic context |
| 2 | COVID Feb 13 | Temporal + Missing Caveat | "as of" → "after", drops uncertainty |
| 3 | Mexico Phase 3 | Fabricated Date | Adds date not in source |
| 4 | COVID Deaths March 19 | Numerical Understatement | Slightly reduces death count |
| 5 | COVID March 24 | Date Shift + Rounding | March 23 → March 24, rounds up |

## CLI Usage

```bash
# Run single case with default jury
python main.py --case 1

# Run all cases
python main.py --case all

# Compare all setups on a case
python main.py --case 2 --compare

# Use specific setup
python main.py --case 1 --setup single
python main.py --case 1 --setup jury-vote
python main.py --case 1 --setup jury-deliberate

# Use different model
python main.py --case 1 --model full

# Verbose output
python main.py --case 1 -v
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Health check |
| `GET /api/cases` | List all test cases |
| `GET /api/cases/{id}` | Get specific case |
| `GET /api/setups` | List available setups |
| `GET /api/models` | List available models |
| `GET /api/debate/stream` | SSE stream of debate events |

### Debate Stream

```
GET /api/debate/stream?case_id=1&setup=jury-llm&model=mini
```

Returns Server-Sent Events:
- `case` - Case details
- `setup` - Setup info
- `agents` - Jury members
- `phase` - Current phase
- `agent_thinking` - Agent is analyzing
- `agent_verdict` - Agent's verdict
- `agent_response` - Deliberation response
- `final_verdict` - Synthesized verdict
- `done` - Stream complete

## Configuration

**config.py**:
```python
MODELS = {
    "mini": "gpt-4.1-mini",   # Fast, cheaper
    "full": "gpt-4.1",        # Best quality
}

SETUPS = {
    "single": {...},
    "jury-vote": {...},
    "jury-llm": {...},
    "jury-deliberate": {...},
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                    (React + Ant Design)                     │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Case      │  │   Setup     │  │   Debate Timeline   │ │
│  │  Selector   │  │  Selector   │  │   (Live Stream)     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │ SSE
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Debate Protocol                         │   │
│  │                                                      │   │
│  │   Phase 1: Independent Analysis                      │   │
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │   │Literalist│ │Contextual│ │Statistic │           │   │
│  │   └──────────┘ └──────────┘ └──────────┘           │   │
│  │                                                      │   │
│  │   Phase 2: Deliberation (optional)                   │   │
│  │                                                      │   │
│  │   Phase 3: Verdict Synthesis                         │   │
│  │   ┌──────────────────────────────────┐              │   │
│  │   │  Majority Vote / LLM Judge       │              │   │
│  │   └──────────────────────────────────┘              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   OpenAI API    │
                    │  (gpt-4.1-mini) │
                    └─────────────────┘
```

## Why Multi-Agent?

A single LLM can answer "is this faithful?" but a jury **explains** it:

1. **Specialization**: Each agent has expertise in specific mutation types
2. **Transparency**: See which aspects triggered concerns
3. **Robustness**: Consensus reduces single-point failures
4. **Explainability**: The debate reveals reasoning, not just a verdict

## Tech Stack

- **Backend**: Python, FastAPI, OpenAI API
- **Frontend**: React, TypeScript, Ant Design, Vite
- **Streaming**: Server-Sent Events (SSE)
- **CLI**: Rich (pretty terminal output)

---

*Cambridge FactTrace Hackathon 2024*
