"""FactTrace Debate Module."""

from debate.protocol import DebateProtocol, SingleAgentBaseline, DebateResult, DebateRound
from debate.verdict import VerdictSynthesizer, FinalVerdict
from debate.crew import FactCheckCrew, CrewDebateResult

__all__ = [
    # Original protocol
    "DebateProtocol",
    "SingleAgentBaseline",
    "DebateResult",
    "DebateRound",
    "VerdictSynthesizer",
    "FinalVerdict",
    # CrewAI-based
    "FactCheckCrew",
    "CrewDebateResult",
]
