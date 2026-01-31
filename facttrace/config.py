"""Configuration for FactTrace multi-agent system."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model Configuration
MODELS = {
    "mini": "gpt-4.1-mini",   # Development/testing
    "full": "gpt-4.1",        # Demo/production
    "cheap": "gpt-4.1-nano",  # Budget option
}

DEFAULT_MODEL = "mini"

# Debate Configuration
MAX_DEBATE_ROUNDS = 1

# Available agent roles
AVAILABLE_AGENTS = ["literalist", "contextualist", "statistician"]

# Setup presets for comparison
SETUPS = {
    "single": {
        "description": "Single agent baseline (no jury)",
        "agents": [],  # Uses SingleAgentBaseline
        "mode": "single",
        "synthesis": None,
        "use_crewai": False,
    },
    "jury-vote": {
        "description": "3-agent jury with majority vote",
        "agents": ["literalist", "contextualist", "statistician"],
        "mode": "one-shot",
        "synthesis": "majority",
        "use_crewai": False,
    },
    "jury-llm": {
        "description": "3-agent jury with LLM synthesis",
        "agents": ["literalist", "contextualist", "statistician"],
        "mode": "one-shot",
        "synthesis": "llm",
        "use_crewai": False,
    },
    "jury-deliberate": {
        "description": "3-agent jury with 1 round of deliberation + LLM synthesis",
        "agents": ["literalist", "contextualist", "statistician"],
        "mode": "deliberation",
        "synthesis": "llm",
        "rounds": 1,
        "use_crewai": False,
    },
    # CrewAI-based setups
    "crew-single": {
        "description": "Single agent using CrewAI",
        "agents": [],
        "mode": "single",
        "synthesis": None,
        "use_crewai": True,
    },
    "crew-jury": {
        "description": "3-agent CrewAI jury with Judge synthesis",
        "agents": ["literalist", "contextualist", "statistician"],
        "mode": "one-shot",
        "synthesis": "llm",
        "use_crewai": True,
    },
}

DEFAULT_SETUP = "crew-jury"
