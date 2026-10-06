"""
Privacy engine for Ines Digital Memory.
Inspects foreground windows and active processes against blacklists
to prevent capturing private chats, banking apps, and credentials.
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Tuple, Dict, Any, List

from core import logger
from core.constants import CONFIGS_DIR

CONFIG_PATH = CONFIGS_DIR / "memory_privacy.yaml"


class PrivacyGuard:
    """Evaluates whether the user's active window/process is sensitive."""

    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load YAML configuration or fall back to defaults."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"Error loading privacy config: {e}")
        return {
            "privacy": {
                "enabled": True,
                "blacklisted_processes": ["whatsapp", "telegram", "signal", "discord", "bitwarden", "1password"],
                "blacklisted_window_titles": ["whatsapp", "telegram", "signal", "discord", "incognito", "bank"],
            }
        }

    def reload(self):
        """Reload configuration from disk."""
        self.config = self._load_config()

    @property
    def enabled(self) -> bool:
        return self.config.get("privacy", {}).get("enabled", True)

    @property
    def blacklisted_processes(self) -> List[str]:
        return [p.lower() for p in self.config.get("privacy", {}).get("blacklisted_processes", [])]

    @property
    def blacklisted_window_titles(self) -> List[str]:
        return [t.lower() for t in self.config.get("privacy", {}).get("blacklisted_window_titles", [])]

    def get_active_window_info(self) -> Tuple[str, str]:
        """
        Get the title and executable process name of the current foreground window.
        Returns (window_title, process_name).
        Uses native Windows ctypes for zero-dependency high speed.
        """
        if sys.platform != "win32":
            return ("Unknown Window", "unknown_process")

        try:
            import ctypes
            from ctypes import wintypes
            import psutil

            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return ("", "")

            # Get Window Title
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            window_title = buf.value

            # Get Process Name
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            process_name = ""
            if pid.value:
                try:
                    proc = psutil.Process(pid.value)
                    process_name = proc.name()
                except Exception:
                    process_name = ""

            return (window_title, process_name)
        except Exception as e:
            logger.debug(f"Could not inspect active window: {e}")
            return ("", "")

    def is_sensitive(self, window_title: str = None, process_name: str = None) -> Tuple[bool, str]:
        """
        Check if the active window or process is considered sensitive.
        If arguments are omitted, inspects the current active window automatically.
        Returns: (is_blocked: bool, reason: str)
        """
        if not self.enabled:
            return (False, "Privacy guard disabled")

        if window_title is None and process_name is None:
            window_title, process_name = self.get_active_window_info()

        title_lower = (window_title or "").lower()
        proc_lower = (process_name or "").lower()

        # Check process blacklist
        for blacklisted_proc in self.blacklisted_processes:
            if blacklisted_proc in proc_lower:
                return (True, f"Blacklisted application: '{process_name}'")

        # Check window title keywords
        for keyword in self.blacklisted_window_titles:
            if keyword in title_lower:
                return (True, f"Sensitive window keyword detected: '{keyword}' in '{window_title}'")

        return (False, "Safe")
