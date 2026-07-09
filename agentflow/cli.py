"""
cli.py - Command-line interface for AgentFlow.

Usage examples:
    python main.py plan "Add JWT-based login with refresh tokens" --session auth
    python main.py docs path/to/file.py
    python main.py review path/to/file.py
    python main.py bugs path/to/file.py
    python main.py improve path/to/file.py
    python main.py chat --session auth
    python main.py sessions
"""

import argparse
import sys

from .llm_client import LLMClient
from .context_manager import ConversationContext
from .planner import generate_plan
from .docgen import generate_docs
from .reviewer import review_code, detect_bugs, suggest_improvements
from .utils import detect_language, read_file, save_output


def _print_and_maybe_save(title: str, content: str, save: str = None, prefix: str = "output"):
    print(f"\n{'=' * 10} {title} {'=' * 10}\n")
    print(content)
    if save:
        path = save_output(content, save, prefix)
        print(f"\n[AgentFlow] Saved to {path}")


def cmd_plan(args):
    client = LLMClient()
    context = ConversationContext(args.session) if args.session else None
    if context:
        context.load()
    requirement = args.requirement
    if args.file:
        requirement = read_file(args.file)
    result = generate_plan(requirement, client, context)
    _print_and_maybe_save("IMPLEMENTATION PLAN", result, args.save, "plan")
    if context:
        context.save()


def cmd_docs(args):
    client = LLMClient()
    context = ConversationContext(args.session) if args.session else None
    if context:
        context.load()
    code = read_file(args.file)
    language = args.language or detect_language(args.file)
    result = generate_docs(code, language, client, context)
    _print_and_maybe_save("TECHNICAL DOCUMENTATION", result, args.save, "docs")
    if context:
        context.save()


def cmd_review(args):
    client = LLMClient()
    context = ConversationContext(args.session) if args.session else None
    if context:
        context.load()
    code = read_file(args.file)
    language = args.language or detect_language(args.file)
    result = review_code(code, language, client, context)
    _print_and_maybe_save("CODE REVIEW", result, args.save, "review")
    if context:
        context.save()


def cmd_bugs(args):
    client = LLMClient()
    context = ConversationContext(args.session) if args.session else None
    if context:
        context.load()
    code = read_file(args.file)
    language = args.language or detect_language(args.file)
    result = detect_bugs(code, language, client, context)
    _print_and_maybe_save("BUG DETECTION", result, args.save, "bugs")
    if context:
        context.save()


def cmd_improve(args):
    client = LLMClient()
    context = ConversationContext(args.session) if args.session else None
    if context:
        context.load()
    code = read_file(args.file)
    language = args.language or detect_language(args.file)
    result = suggest_improvements(code, language, client, context)
    _print_and_maybe_save("IMPROVEMENT SUGGESTIONS", result, args.save, "improve")
    if context:
        context.save()


def cmd_chat(args):
    """Free-form interactive chat that keeps conversational context across turns."""
    client = LLMClient()
    context = ConversationContext(args.session or "chat")
    context.load()
    print("[AgentFlow] Interactive chat. Type 'exit' or 'quit' to leave.\n")
    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue
        reply = client.generate(user_input, context=context)
        print(f"\nagentflow> {reply}\n")
        context.save()


def cmd_sessions(args):
    sessions = ConversationContext.list_sessions()
    if not sessions:
        print("[AgentFlow] No saved sessions yet.")
        return
    print("[AgentFlow] Saved sessions:")
    for s in sessions:
        print(f"  - {s}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentflow",
        description="AgentFlow - AI Software Engineering Assistant (powered by Gemini)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_plan = sub.add_parser("plan", help="Convert a requirement into an implementation plan")
    p_plan.add_argument("requirement", nargs="?", default="", help="Requirement text")
    p_plan.add_argument("--file", help="Read requirement text from a file instead")
    p_plan.add_argument("--session", help="Session name to keep conversational context")
    p_plan.add_argument("--save", help="Directory to save output as a Markdown file")
    p_plan.set_defaults(func=cmd_plan)

    p_docs = sub.add_parser("docs", help="Generate technical documentation for a code file")
    p_docs.add_argument("file", help="Path to source code file")
    p_docs.add_argument("--language", help="Override auto-detected language")
    p_docs.add_argument("--session", help="Session name to keep conversational context")
    p_docs.add_argument("--save", help="Directory to save output as a Markdown file")
    p_docs.set_defaults(func=cmd_docs)

    p_review = sub.add_parser("review", help="Run an automated code review on a file")
    p_review.add_argument("file", help="Path to source code file")
    p_review.add_argument("--language", help="Override auto-detected language")
    p_review.add_argument("--session", help="Session name to keep conversational context")
    p_review.add_argument("--save", help="Directory to save output as a Markdown file")
    p_review.set_defaults(func=cmd_review)

    p_bugs = sub.add_parser("bugs", help="Run automated bug detection on a file")
    p_bugs.add_argument("file", help="Path to source code file")
    p_bugs.add_argument("--language", help="Override auto-detected language")
    p_bugs.add_argument("--session", help="Session name to keep conversational context")
    p_bugs.add_argument("--save", help="Directory to save output as a Markdown file")
    p_bugs.set_defaults(func=cmd_bugs)

    p_improve = sub.add_parser("improve", help="Get code improvement suggestions for a file")
    p_improve.add_argument("file", help="Path to source code file")
    p_improve.add_argument("--language", help="Override auto-detected language")
    p_improve.add_argument("--session", help="Session name to keep conversational context")
    p_improve.add_argument("--save", help="Directory to save output as a Markdown file")
    p_improve.set_defaults(func=cmd_improve)

    p_chat = sub.add_parser("chat", help="Interactive free-form chat with conversational memory")
    p_chat.add_argument("--session", help="Session name to keep conversational context")
    p_chat.set_defaults(func=cmd_chat)

    p_sessions = sub.add_parser("sessions", help="List saved sessions")
    p_sessions.set_defaults(func=cmd_sessions)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except RuntimeError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
