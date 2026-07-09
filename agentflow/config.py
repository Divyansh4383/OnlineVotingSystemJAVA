"""
config.py - Centralized configuration for AgentFlow.

Loads the Gemini API key from the environment (or a local .env file)
and exposes model/generation defaults used across the app.
"""

import os
import sys

DEFAULT_MODEL = "gemini-2.5-flash"  # Free-tier friendly model on Google AI Studio


def _load_dotenv(path: str = ".env") -> None:
    """Minimal .env loader (avoids adding a hard dependency on python-dotenv)."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


MISSING_KEY_MESSAGE = (
    "No Gemini API key found. Get a free key at https://aistudio.google.com/apikey "
    "and set it via (1) an environment variable GEMINI_API_KEY, or (2) a .env file "
    "in the project root containing GEMINI_API_KEY=your-key-here."
)


def get_api_key() -> str:
    """
    Returns the Gemini API key, checking (in order):
      1. GEMINI_API_KEY environment variable
      2. A .env file in the current working directory
    Raises RuntimeError with a helpful message if no key is found — callers
    (CLI or web server) decide how to surface that (exit vs. JSON error),
    so this module never kills a long-running process like the web server.
    """
    _load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(MISSING_KEY_MESSAGE)
    return api_key


class Settings:
    """App-wide defaults. Kept in one place so behavior is easy to tune."""
    MODEL = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    TEMPERATURE = float(os.environ.get("GEMINI_TEMPERATURE", 0.4))
    MAX_OUTPUT_TOKENS = int(os.environ.get("GEMINI_MAX_TOKENS", 4096))
    SESSION_DIR = os.environ.get("AGENTFLOW_SESSION_DIR", ".agentflow_sessions")
