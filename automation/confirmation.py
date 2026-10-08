"""
Confirmation prompt flow for Megan automation.
Ensures destructive or sensitive actions require explicit user consent
before execution.
"""

from typing import Optional

from core import config, logger


class ConfirmationManager:
    """
    Handles user confirmation for sensitive actions.
    Supports both CLI and API modes.
    """

    def __init__(self, require_confirmation: bool = True):
        self.require_confirmation = require_confirmation

    def confirm_cli(self, action_description: str) -> bool:
        """
        Prompt the user for confirmation in CLI mode.

        Args:
            action_description: Human-readable description of the action.

        Returns:
            True if user confirms, False otherwise.
        """
        if not self.require_confirmation:
            return True

        print(f"\n⚠️  Megan wants to perform a potentially destructive action:")
        print(f"   {action_description}")
        print()

        try:
            response = input("   Allow this action? [y/N]: ").strip().lower()
            if response in ("y", "yes"):
                logger.info(f"User confirmed action: {action_description}")
                return True
            else:
                logger.info(f"User denied action: {action_description}")
                print("   ❌ Action cancelled.")
                return False
        except (EOFError, KeyboardInterrupt):
            print("\n   ❌ Action cancelled.")
            return False

    def confirm_api(self, action_description: str) -> dict:
        """
        Generate a confirmation request for the API/frontend.
        The frontend renders a confirmation dialog and sends back the decision.

        Args:
            action_description: What Megan wants to do.

        Returns:
            Dict with confirmation_required=True and the description.
        """
        return {
            "confirmation_required": True,
            "action_description": action_description,
            "message": f"Megan wants to: {action_description}. Allow?",
        }
