"""
Session management for Megan.
Creates, lists, and resumes conversation sessions.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from core import logger
from core.constants import CONVERSATIONS_DIR
from chatbot.history import ConversationHistory


def new_session() -> ConversationHistory:
    """
    Create a brand-new session with a unique ID.

    Returns:
        An empty ConversationHistory ready to use.
    """
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    logger.info(f"New session created: {session_id}")
    return ConversationHistory(session_id)


def resume_session(session_id: str) -> Optional[ConversationHistory]:
    """
    Load an existing session from disk.

    Args:
        session_id: The ID of the session to resume.

    Returns:
        A ConversationHistory loaded with past messages,
        or None if the session does not exist.
    """
    history = ConversationHistory(session_id)
    if history.load():
        return history
    logger.warning(f"Session not found: '{session_id}'")
    return None


def list_sessions() -> list[dict]:
    """
    List all saved sessions ordered by most recent first.

    Returns:
        List of dicts with session_id, updated_at, and message_count.
    """
    sessions = []
    for path in sorted(CONVERSATIONS_DIR.glob("*.json"), reverse=True):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            sessions.append({
                "session_id": data.get("session_id", path.stem),
                "updated_at": data.get("updated_at", "unknown"),
                "message_count": len(data.get("messages", [])),
            })
        except Exception:
            continue
    return sessions


def delete_session(session_id: str) -> bool:
    """
    Delete a saved session file.

    Returns:
        True if deleted, False if not found.
    """
    path = CONVERSATIONS_DIR / f"{session_id}.json"
    if path.exists():
        path.unlink()
        logger.info(f"Deleted session: {session_id}")
        return True
    return False


def print_sessions() -> None:
    """Pretty-print all saved sessions to the terminal."""
    sessions = list_sessions()
    if not sessions:
        print("No saved sessions found.")
        return
    print(f"{'Session ID':<35} {'Updated':<25} {'Messages'}")
    print("-" * 70)
    for s in sessions:
        print(f"{s['session_id']:<35} {s['updated_at'][:19]:<25} {s['message_count']}")
