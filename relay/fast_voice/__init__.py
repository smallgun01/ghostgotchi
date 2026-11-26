"""Vendored from Grok-Amusant fast_voice (MIT). See third_party/NOTICE.md."""
from .contracts import AudioFrame, CLIENT_INPUT_RATE_HZ, CLIENT_OUTPUT_RATE_HZ, ProviderError, TurnCompleteEvent
from .gemini import GeminiLiveProvider

__all__ = [
    "AudioFrame", "CLIENT_INPUT_RATE_HZ", "CLIENT_OUTPUT_RATE_HZ",
    "ProviderError", "TurnCompleteEvent", "GeminiLiveProvider",
]
