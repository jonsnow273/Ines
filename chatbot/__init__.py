"""
Chatbot module — Conversation management for Ines.

Provides:
- ConversationHistory: per-session message storage with auto-save
- Session management: new_session(), resume_session(), list_sessions()
- ContextManager: automatic token-limit trimming
- LanguageManager: multilingual system prompt loading

Quick usage:
    from chatbot import new_session, ContextManager, load_system_prompt

    history = new_session()
    history.add_system(load_system_prompt("hi"))
    history.add("user", "Namaste!")
"""

from chatbot.history import ConversationHistory
from chatbot.session import new_session, resume_session, list_sessions, delete_session, print_sessions
from chatbot.context_manager import ContextManager
from chatbot.language_manager import load_system_prompt, is_supported, list_supported, SUPPORTED_LANGUAGES

__all__ = [
    "ConversationHistory",
    "new_session",
    "resume_session",
    "list_sessions",
    "delete_session",
    "print_sessions",
    "ContextManager",
    "load_system_prompt",
    "is_supported",
    "list_supported",
    "SUPPORTED_LANGUAGES",
]
