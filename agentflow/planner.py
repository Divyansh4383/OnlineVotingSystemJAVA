"""
planner.py - Converts software requirements into structured implementation plans.
"""

from .llm_client import LLMClient
from .prompts import PLAN_TEMPLATE, build_prompt
from .context_manager import ConversationContext


def generate_plan(requirement: str, client: LLMClient, context: ConversationContext = None) -> str:
    prompt = build_prompt(PLAN_TEMPLATE, requirement=requirement)
    return client.generate(prompt, context=context)
