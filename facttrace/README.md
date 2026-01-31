# FactTrace - Multi-Agent Fact Verification System

A "jury of AI agents" that debates whether external claims are faithful representations of source facts, or mutations.

## Overview

FactTrace uses multiple specialized AI agents to analyze claims against source texts. Each agent brings a different perspective, and through structured debate, they reach a consensus verdict on whether a claim is **faithful** or a **mutation** of the original facts.

## Installation

```bash
cd facttrace
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the `facttrace` directory:

```
OPENAI_API_KEY=your-api-key-here
```

## Usage

```bash
# Run a single case
python main.py --case 1

# Run all cases
python main.py --case all

# Use GPT-4o instead of GPT-4o-mini
python main.py --case 1 --model full

# Verbose mode (show detailed debate)
python main.py --case 1 --verbose
```

## The Agent Jury

### Literalist (Red)
Verifies exact factual accuracy. Checks if numbers, dates, and specific details in the claim precisely match the source. Any deviation in hard facts is flagged as a potential mutation.

### Contextualist (Blue)
Examines whether important context is preserved. Looks for missing caveats, omitted qualifiers, and contextual information that changes the meaning or implications of the facts.

### Statistician (Green)
Analyzes numerical claims and their framing. Checks for rounding errors, misleading comparisons, temporal precision issues, and whether statistics are presented fairly.

## How It Works

1. **Independent Analysis**: Each agent independently analyzes the claim against the source
2. **Share Verdicts**: Agents present their initial verdicts with reasoning
3. **Debate Rounds**: Agents can respond to and challenge each other's conclusions
4. **Synthesis**: A final verdict is synthesized from the debate

## Test Cases

The system includes 5 pre-selected cases demonstrating different mutation types:
- Framing Flip
- Temporal + Missing Caveat
- Fabricated Date
- Numerical Understatement
- Date Shift + Rounding

---

*Built for the Cambridge Hackathon*
