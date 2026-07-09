"""
context_manager.py - Maintains conversational context across turns and
allows sessions to be saved/loaded from disk, so a session can be resumed
later (e.g. continuing a plan discussion across CLI invocations).
"""

import json
import os
import time
from typing import List, Dict

from .config import Settings


class ConversationContext:
    """
    Stores turn-by-turn history in the same shape the Gemini API expects,
    so it can be replayed directly as conversation context on each call.
    """

    def __init__(self, session_name: str = "default"):
        self.session_name = session_name
        self.history: List[Dict] = []
        os.makedirs(Settings.SESSION_DIR, exist_ok=True)
        self._path = os.path.join(Settings.SESSION_DIR, f"{session_name}.json")

    def add_user_turn(self, text: str) -> None:
        self.history.append({"role": "user", "parts": [{"text": text}]})

    def add_model_turn(self, text: str) -> None:
        self.history.append({"role": "model", "parts": [{"text": text}]})

    def as_contents(self) -> List[Dict]:
        """Return history in the format expected by the Gemini `contents` field."""
        return self.history

    def save(self) -> None:
        payload = {
            "session_name": self.session_name,
            "updated_at": time.time(),
            "history": self.history,
        }
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def load(self) -> bool:
        """Load a previously saved session. Returns True if a session was found."""
        if not os.path.exists(self._path):
            return False
        with open(self._path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        self.history = payload.get("history", [])
        return True

    def clear(self) -> None:
        self.history = []
        if os.path.exists(self._path):
            os.remove(self._path)

    @staticmethod
    def list_sessions() -> List[str]:
        if not os.path.isdir(Settings.SESSION_DIR):
            return []
        return sorted(
            f[:-5] for f in os.listdir(Settings.SESSION_DIR) if f.endswith(".json")
        )
