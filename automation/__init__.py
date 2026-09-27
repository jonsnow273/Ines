"""
Automation module — PC action execution for Sephora.

Provides:
- WhitelistManager: validates actions against the safety whitelist
- ConfirmationManager: prompts user before destructive operations
- ActionHandler: executes whitelisted PC actions (files, apps, URLs)

Quick usage:
    from automation import ActionHandler

    handler = ActionHandler()
    result = handler.execute("file_operations", "open", path="C:/Users/test.txt")
    result = handler.execute("web_actions", "search_web", query="python tutorials")
"""

from automation.whitelist import WhitelistManager
from automation.confirmation import ConfirmationManager
from automation.action_handler import ActionHandler

__all__ = [
    "WhitelistManager",
    "ConfirmationManager",
    "ActionHandler",
]
