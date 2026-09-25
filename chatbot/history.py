"""
Conversation history manager for Sephora.
Saves and loads message lists as JSON per session.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from core import logger
from core.constants import CONVERSATIONS_DIR


class ConversationHistory:
    """
    Manages the in-memory message list and persists it to disk
    as a JSON file keyed by session ID.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: list[dict] = []
        self._path = CONVERSATIONS_DIR / f"{session_id}.json"

    def add(self, role: str, content: str) -> None:
        """Append a message and auto-save to disk."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        self._save()

    def add_system(self, content: str) -> None:
        """Prepend a system prompt. Replaces any existing system message."""
        self.messages = [m for m in self.messages if m["role"] != "system"]
        self.messages.insert(0, {
            "role": "system",
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        self._save()

    def to_llm_format(self) -> list[dict]:
        """Return messages in the role/content format the LLM expects."""
        return [{"role": m["role"], "content": m["content"]} for m in self.messages]

    def clear(self) -> None:
        """Clear in-memory history (does not delete the file)."""
        self.messages = []

    def _save(self) -> None:
        """Persist current messages to disk."""
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump({
                    "session_id": self.session_id,
                    "updated_at": datetime.now().isoformat(),
                    "messages": self.messages,
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save conversation history: {e}")

    def load(self) -> bool:
        """Load history from disk. Returns True if found."""
        if not self._path.exists():
            return False
        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            self.messages = data.get("messages", [])
            logger.info(f"Loaded session '{self.session_id}' ({len(self.messages)} messages)")
            return True
        except Exception as e:
            logger.warning(f"Failed to load session '{self.session_id}': {e}")
            return False

    def delete(self) -> None:
        """Delete this session's file from disk."""
        if self._path.exists():
            self._path.unlink()
            logger.info(f"Deleted session file: {self._path}")

    def __len__(self) -> int:
        return len(self.messages)

    def __repr__(self) -> str:
        return f"<ConversationHistory session='{self.session_id}' messages={len(self.messages)}>"
