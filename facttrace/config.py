"""Configuration for Galileo multi-agent fact verification system."""

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
MAX_DEBATE_ROUNDS = 10

# Available agent roles (3 heated debaters)
AVAILABLE_AGENTS = ["data_scientist", "philosopher", "physicist"]

# ============== ITERATIVE MULTI-ROUND DEBATE ==============
# Three specialists debate in rounds until consensus.
# The Philosopher is adversarial - always argues the opposite.

SETUPS = {
    "iterative": {
        "description": "Iterative debate: up to 10 rounds with majority consensus stopping",
        "paradigm": "iterative",
        "agents": ["data_scientist", "philosopher", "physicist"],
        "mode": "iterative",
        "rounds": 10,
        "adaptive_stop": True,
        "consensus_type": "majority",
        "synthesis": "judge",
        "use_crewai": True,
    },
}

DEFAULT_SETUP = "iterative"
