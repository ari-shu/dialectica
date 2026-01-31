"""Configuration for FactTrace multi-agent system."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model Configuration
MODELS = {
    "mini": "gpt-4o-mini",  # Development/testing
    "full": "gpt-4o",        # Demo/production
}

DEFAULT_MODEL = "mini"

# Debate Configuration
MAX_DEBATE_ROUNDS = 2
AGENTS_ENABLED = ["literalist", "contextualist", "statistician"]
