"""
utils.py - Small shared helpers used by the CLI and feature modules.
"""

import os
import sys
from datetime import datetime

EXT_LANGUAGE_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript", ".java": "java",
    ".cpp": "cpp", ".c": "c", ".cs": "csharp", ".go": "go", ".rb": "ruby",
    ".php": "php", ".rs": "rust", ".kt": "kotlin", ".swift": "swift",
    ".html": "html", ".css": "css", ".sql": "sql", ".sh": "bash",
}


def detect_language(file_path: str) -> str:
    _, ext = os.path.splitext(file_path)
    return EXT_LANGUAGE_MAP.get(ext.lower(), "text")


def read_file(file_path: str) -> str:
    if not os.path.isfile(file_path):
        sys.exit(f"[AgentFlow] ERROR: File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def save_output(content: str, out_dir: str, prefix: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"{prefix}_{timestamp}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
