"""
PC action handler for Sephora.
Executes whitelisted automation actions like opening apps, files,
and URLs with safety checks and user confirmation.
"""

import os
import subprocess
import platform
import webbrowser
from pathlib import Path
from typing import Optional

from core import logger
from automation.whitelist import WhitelistManager
from automation.confirmation import ConfirmationManager


class ActionHandler:
    """
    Executes PC automation actions after validating against the whitelist
    and obtaining user confirmation for destructive operations.

    Usage:
        handler = ActionHandler()
        result = handler.execute("file_operations", "open", path="/path/to/file")
    """

    def __init__(self, require_confirmation: bool = True):
        self.whitelist = WhitelistManager()
        self.confirmation = ConfirmationManager(require_confirmation)

    def execute(self, category: str, action: str, **kwargs) -> dict:
        """
        Execute an automation action.

        Args:
            category: Action category (e.g. 'file_operations').
            action: Specific action (e.g. 'open').
            **kwargs: Action-specific parameters (e.g. path, app_name, url).

        Returns:
            Dict with 'success', 'message', and optionally 'data'.
        """
        # Step 1: Check whitelist
        if not self.whitelist.is_allowed(category, action):
            msg = f"Action '{action}' in '{category}' is not allowed by whitelist."
            logger.warning(msg)
            return {"success": False, "message": msg}

        # Step 2: Confirm destructive actions
        if self.whitelist.is_destructive(category, action):
            desc = self._describe_action(category, action, **kwargs)
            if not self.confirmation.confirm_cli(desc):
                return {"success": False, "message": "Action cancelled by user."}

        # Step 3: Route to handler
        try:
            handler_map = {
                ("file_operations", "open"): self._open_file,
                ("file_operations", "read"): self._read_file,
                ("file_operations", "list"): self._list_directory,
                ("file_operations", "search"): self._search_files,
                ("application_control", "open_app"): self._open_app,
                ("application_control", "close_app"): self._close_app,
                ("web_actions", "open_url"): self._open_url,
                ("web_actions", "search_web"): self._search_web,
            }

            handler_fn = handler_map.get((category, action))
            if handler_fn is None:
                return {"success": False, "message": f"No handler for '{category}.{action}'."}

            return handler_fn(**kwargs)

        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {"success": False, "message": f"Execution error: {str(e)}"}

    def _describe_action(self, category: str, action: str, **kwargs) -> str:
        """Generate a human-readable description for confirmation prompts."""
        if category == "file_operations":
            path = kwargs.get("path", "unknown")
            return f"{action} file: {path}"
        elif category == "application_control":
            app = kwargs.get("app_name", "unknown")
            return f"{action}: {app}"
        return f"{category}.{action}"

    # ── File Operations ─────────────────────────────────────────────

    def _open_file(self, path: str = "", **kwargs) -> dict:
        """Open a file with the system default application."""
        if not path or not Path(path).exists():
            return {"success": False, "message": f"File not found: {path}"}
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", path], check=True)
            else:
                subprocess.run(["xdg-open", path], check=True)
            logger.info(f"Opened file: {path}")
            return {"success": True, "message": f"Opened: {path}"}
        except Exception as e:
            return {"success": False, "message": f"Failed to open: {e}"}

    def _read_file(self, path: str = "", max_chars: int = 5000, **kwargs) -> dict:
        """Read and return the contents of a text file."""
        if not path or not Path(path).exists():
            return {"success": False, "message": f"File not found: {path}"}
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                content = f.read(max_chars)
            logger.info(f"Read file: {path} ({len(content)} chars)")
            return {"success": True, "message": f"Read {len(content)} chars.", "data": content}
        except Exception as e:
            return {"success": False, "message": f"Failed to read: {e}"}

    def _list_directory(self, path: str = ".", **kwargs) -> dict:
        """List files and folders in a directory."""
        target = Path(path)
        if not target.exists() or not target.is_dir():
            return {"success": False, "message": f"Directory not found: {path}"}
        try:
            items = []
            for item in sorted(target.iterdir()):
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                })
            logger.info(f"Listed directory: {path} ({len(items)} items)")
            return {"success": True, "message": f"{len(items)} items.", "data": items}
        except Exception as e:
            return {"success": False, "message": f"Failed to list: {e}"}

    def _search_files(self, path: str = ".", pattern: str = "*", **kwargs) -> dict:
        """Search for files matching a glob pattern."""
        target = Path(path)
        if not target.exists():
            return {"success": False, "message": f"Path not found: {path}"}
        try:
            matches = [str(p) for p in target.rglob(pattern)][:50]
            logger.info(f"Search '{pattern}' in {path}: {len(matches)} results")
            return {"success": True, "message": f"{len(matches)} matches.", "data": matches}
        except Exception as e:
            return {"success": False, "message": f"Search failed: {e}"}

    # ── Application Control ─────────────────────────────────────────

    def _open_app(self, app_name: str = "", **kwargs) -> dict:
        """Open an application by name."""
        if not app_name:
            return {"success": False, "message": "No app name provided."}
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["start", "", app_name], shell=True)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", "-a", app_name])
            else:
                subprocess.Popen([app_name])
            logger.info(f"Opened application: {app_name}")
            return {"success": True, "message": f"Opened: {app_name}"}
        except Exception as e:
            return {"success": False, "message": f"Failed to open app: {e}"}

    def _close_app(self, app_name: str = "", **kwargs) -> dict:
        """Close an application by name (Windows only for now)."""
        if not app_name:
            return {"success": False, "message": "No app name provided."}
        try:
            if platform.system() == "Windows":
                subprocess.run(["taskkill", "/IM", app_name, "/F"],
                               capture_output=True, check=True)
            else:
                subprocess.run(["pkill", "-f", app_name],
                               capture_output=True, check=True)
            logger.info(f"Closed application: {app_name}")
            return {"success": True, "message": f"Closed: {app_name}"}
        except subprocess.CalledProcessError:
            return {"success": False, "message": f"App not running or access denied: {app_name}"}

    # ── Web Actions ─────────────────────────────────────────────────

    def _open_url(self, url: str = "", **kwargs) -> dict:
        """Open a URL in the default browser."""
        if not url:
            return {"success": False, "message": "No URL provided."}
        try:
            webbrowser.open(url)
            logger.info(f"Opened URL: {url}")
            return {"success": True, "message": f"Opened: {url}"}
        except Exception as e:
            return {"success": False, "message": f"Failed to open URL: {e}"}

    def _search_web(self, query: str = "", **kwargs) -> dict:
        """Open a web search in the default browser."""
        if not query:
            return {"success": False, "message": "No search query provided."}
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            logger.info(f"Web search: {query}")
            return {"success": True, "message": f"Searching: {query}"}
        except Exception as e:
            return {"success": False, "message": f"Search failed: {e}"}
