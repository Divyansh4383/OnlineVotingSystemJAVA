"""
docgen.py - Generates technical documentation from source code.
"""

from .llm_client import LLMClient
from .prompts import DOC_TEMPLATE, build_prompt
from .context_manager import ConversationContext


def generate_docs(code: str, language: str, client: LLMClient, context: ConversationContext = None) -> str:
    prompt = build_prompt(DOC_TEMPLATE, code=code, language=language)
    return client.generate(prompt, context=context)
