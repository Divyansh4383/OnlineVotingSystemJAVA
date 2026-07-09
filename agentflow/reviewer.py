"""
reviewer.py - Automated code review, bug detection, and improvement suggestions.
"""

from .llm_client import LLMClient
from .prompts import (
    CODE_REVIEW_TEMPLATE,
    BUG_DETECTION_TEMPLATE,
    IMPROVEMENT_TEMPLATE,
    build_prompt,
)
from .context_manager import ConversationContext


def review_code(code: str, language: str, client: LLMClient, context: ConversationContext = None) -> str:
    prompt = build_prompt(CODE_REVIEW_TEMPLATE, code=code, language=language)
    return client.generate(prompt, context=context)


def detect_bugs(code: str, language: str, client: LLMClient, context: ConversationContext = None) -> str:
    prompt = build_prompt(BUG_DETECTION_TEMPLATE, code=code, language=language)
    return client.generate(prompt, context=context)


def suggest_improvements(code: str, language: str, client: LLMClient, context: ConversationContext = None) -> str:
    prompt = build_prompt(IMPROVEMENT_TEMPLATE, code=code, language=language)
    return client.generate(prompt, context=context)
