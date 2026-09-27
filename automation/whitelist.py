"""
Whitelist manager for Sephora automation.
Loads permitted actions from automation_whitelist.yaml and validates
user requests before execution.
"""

from pathlib import Path
from typing import Optional

from core import config, logger
from core.constants import WHITELIST_CONFIG_PATH


# Default whitelist if no YAML file exists
DEFAULT_WHITELIST = {
    "file_operations": {
        "enabled": True,
        "allowed": ["open", "read", "list", "search"],
        "blocked": ["delete", "format", "overwrite"],
    },
    "application_control": {
        "enabled": True,
        "allowed": ["open_app", "close_app", "switch_app"],
        "blocked": ["install", "uninstall"],
    },
    "system_commands": {
        "enabled": False,
        "allowed": [],
        "blocked": ["shutdown", "restart", "registry_edit", "disk_format"],
    },
    "web_actions": {
        "enabled": True,
        "allowed": ["open_url", "search_web"],
        "blocked": ["download_file", "execute_script"],
    },
}


class WhitelistManager:
    """
    Manages the set of actions Sephora is allowed to perform.
    Actions not on the whitelist are blocked by default.
    """

    def __init__(self):
        self.whitelist: dict = {}
        self._load()

    def _load(self) -> None:
        """Load whitelist from YAML config, falling back to defaults."""
        try:
            import yaml
            if WHITELIST_CONFIG_PATH.exists():
                with open(WHITELIST_CONFIG_PATH, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                self.whitelist = data.get("whitelist", data)
                logger.info(f"Automation whitelist loaded from {WHITELIST_CONFIG_PATH}")
            else:
                self.whitelist = DEFAULT_WHITELIST
                logger.info("Using default automation whitelist.")
        except ImportError:
            self.whitelist = DEFAULT_WHITELIST
            logger.warning("PyYAML not installed. Using default whitelist.")
        except Exception as e:
            self.whitelist = DEFAULT_WHITELIST
            logger.warning(f"Failed to load whitelist: {e}. Using defaults.")

    def is_allowed(self, category: str, action: str) -> bool:
        """
        Check if a specific action is allowed.

        Args:
            category: Action category (e.g. 'file_operations', 'application_control').
            action: Specific action name (e.g. 'open', 'delete').

        Returns:
            True if the action is permitted.
        """
        cat = self.whitelist.get(category)
        if cat is None:
            logger.warning(f"Unknown action category: '{category}'")
            return False

        if not cat.get("enabled", False):
            logger.debug(f"Category '{category}' is disabled.")
            return False

        blocked = cat.get("blocked", [])
        if action in blocked:
            logger.warning(f"Action '{action}' is blocked in '{category}'.")
            return False

        allowed = cat.get("allowed", [])
        if action in allowed:
            return True

        # If not explicitly allowed, default to blocked (safe by default)
        logger.debug(f"Action '{action}' not in allowed list for '{category}'.")
        return False

    def is_destructive(self, category: str, action: str) -> bool:
        """
        Check if an action is considered destructive (requires confirmation).
        """
        destructive_actions = {
            "file_operations": ["delete", "overwrite", "move", "rename"],
            "application_control": ["close_app", "uninstall", "kill_process"],
            "system_commands": ["shutdown", "restart", "registry_edit"],
            "web_actions": ["download_file"],
        }
        return action in destructive_actions.get(category, [])

    def get_categories(self) -> list[str]:
        """Return all configured action categories."""
        return list(self.whitelist.keys())

    def get_allowed_actions(self, category: str) -> list[str]:
        """Return the list of allowed actions for a category."""
        cat = self.whitelist.get(category, {})
        if not cat.get("enabled", False):
            return []
        return cat.get("allowed", [])
