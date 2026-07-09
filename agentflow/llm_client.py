"""
llm_client.py - Thin wrapper around the Gemini API (google-genai SDK).

Centralizing the API call here means every feature module (planner, docgen,
reviewer) goes through one consistent client with shared error handling,
retry logic, and conversation-context support.
"""

import time
from typing import Optional

from google import genai
from google.genai import types
from google.genai.errors import APIError

from .config import Settings, get_api_key
from .prompts import BASE_SYSTEM_INSTRUCTION
from .context_manager import ConversationContext


class LLMClient:
    def __init__(self, model: Optional[str] = None):
        self.client = genai.Client(api_key=get_api_key())
        self.model = model or Settings.MODEL

    def generate(
        self,
        prompt: str,
        context: Optional[ConversationContext] = None,
        system_instruction: str = BASE_SYSTEM_INSTRUCTION,
        max_retries: int = 3,
    ) -> str:
        """
        Sends `prompt` to Gemini. If `context` is provided, prior turns are
        included so the model keeps conversational memory, and the new
        exchange is appended back into the context.
        """
        contents = list(context.as_contents()) if context else []
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=Settings.TEMPERATURE,
            max_output_tokens=Settings.MAX_OUTPUT_TOKENS,
        )

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )
                text = response.text or ""
                if context:
                    context.add_user_turn(prompt)
                    context.add_model_turn(text)
                return text
            except APIError as e:
                last_error = e
                # Simple exponential backoff for transient/rate-limit errors
                time.sleep(min(2 ** attempt, 10))
            except Exception as e:  # noqa: BLE001 - surface any other client error
                last_error = e
                break

        raise RuntimeError(
            f"[AgentFlow] Gemini API call failed after {max_retries} attempts: {last_error}"
        )
