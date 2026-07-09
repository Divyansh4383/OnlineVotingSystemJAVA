"""
webapp.py - Flask API for the AgentFlow web frontend.

This is a thin HTTP layer over the existing agentflow package (planner,
docgen, reviewer, context_manager) — the same modules the CLI uses. No
business logic lives here; every route just validates input, calls into
agentflow, and returns JSON.
"""

from flask import Flask, request, jsonify, send_from_directory
import os

from agentflow.llm_client import LLMClient
from agentflow.context_manager import ConversationContext
from agentflow.planner import generate_plan
from agentflow.docgen import generate_docs
from agentflow.reviewer import review_code, detect_bugs, suggest_improvements

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")


def _session_for(name: str) -> ConversationContext:
    context = ConversationContext(name or "default")
    context.load()
    return context


def _handle(fn):
    """Run a feature function, translating any failure into a clean JSON error
    instead of a stack trace, and never crashing the server process."""
    try:
        result = fn()
        return jsonify({"ok": True, "result": result})
    except RuntimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:  # noqa: BLE001 - last line of defense for the API
        return jsonify({"ok": False, "error": f"Unexpected error: {e}"}), 500


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/api/health")
def health():
    return jsonify({"ok": True})


@app.route("/api/sessions")
def sessions():
    return jsonify({"ok": True, "sessions": ConversationContext.list_sessions()})


@app.route("/api/plan", methods=["POST"])
def api_plan():
    data = request.get_json(force=True) or {}
    requirement = (data.get("requirement") or "").strip()
    session_name = data.get("session") or ""

    def run():
        if not requirement:
            raise RuntimeError("Please enter a requirement to turn into a plan.")
        client = LLMClient()
        context = _session_for(session_name) if session_name else None
        result = generate_plan(requirement, client, context)
        if context:
            context.save()
        return result

    return _handle(run)


@app.route("/api/docs", methods=["POST"])
def api_docs():
    data = request.get_json(force=True) or {}
    code = (data.get("code") or "").strip()
    language = data.get("language") or "text"
    session_name = data.get("session") or ""

    def run():
        if not code:
            raise RuntimeError("Please paste some code to document.")
        client = LLMClient()
        context = _session_for(session_name) if session_name else None
        result = generate_docs(code, language, client, context)
        if context:
            context.save()
        return result

    return _handle(run)


def _code_route(feature_fn, empty_message):
    data = request.get_json(force=True) or {}
    code = (data.get("code") or "").strip()
    language = data.get("language") or "text"
    session_name = data.get("session") or ""

    def run():
        if not code:
            raise RuntimeError(empty_message)
        client = LLMClient()
        context = _session_for(session_name) if session_name else None
        result = feature_fn(code, language, client, context)
        if context:
            context.save()
        return result

    return _handle(run)


@app.route("/api/review", methods=["POST"])
def api_review():
    return _code_route(review_code, "Please paste some code to review.")


@app.route("/api/bugs", methods=["POST"])
def api_bugs():
    return _code_route(detect_bugs, "Please paste some code to scan for bugs.")


@app.route("/api/improve", methods=["POST"])
def api_improve():
    return _code_route(suggest_improvements, "Please paste some code to get improvement suggestions.")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()
    session_name = data.get("session") or "chat"

    def run():
        if not message:
            raise RuntimeError("Please enter a message.")
        client = LLMClient()
        context = _session_for(session_name)
        result = client.generate(message, context=context)
        context.save()
        return result

    return _handle(run)


@app.route("/api/sessions/<name>", methods=["DELETE"])
def api_clear_session(name):
    def run():
        context = ConversationContext(name)
        context.clear()
        return "cleared"

    return _handle(run)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[AgentFlow] Web UI running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
