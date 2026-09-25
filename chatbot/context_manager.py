"""
Context window manager for Sephora.
Trims conversation history to stay within the model's token limit.
"""

from typing import Optional

from core import config, logger


class ContextManager:
    """
    Monitors and trims the active message list to prevent
    exceeding the model's maximum context length.

    Strategy:
    - Count tokens before each generation call.
    - If over the threshold, remove the oldest user/assistant message pairs.
    - The system message (index 0) is NEVER removed.
    """

    def __init__(self, tokenizer_wrapper=None, max_tokens: Optional[int] = None):
        self.tokenizer_wrapper = tokenizer_wrapper
        self.max_tokens = max_tokens or config.max_context_tokens

    def count_tokens(self, messages: list[dict]) -> int:
        """
        Count the total tokens in a list of messages.
        Falls back to a character-based estimate if tokenizer is unavailable.
        """
        if self.tokenizer_wrapper is None:
            # Rough estimate: ~4 chars per token
            total_chars = sum(len(m.get("content", "")) for m in messages)
            return total_chars // 4

        try:
            combined = " ".join(m.get("content", "") for m in messages)
            tokens = self.tokenizer_wrapper.tokenizer(
                combined, return_tensors="pt", truncation=False
            )
            return tokens["input_ids"].shape[1]
        except Exception:
            total_chars = sum(len(m.get("content", "")) for m in messages)
            return total_chars // 4

    def trim(self, messages: list[dict]) -> list[dict]:
        """
        Trim the message list to stay within the token limit.
        Removes the oldest non-system messages first.

        Args:
            messages: Full conversation history.

        Returns:
            Trimmed message list (system prompt always preserved).
        """
        if self.count_tokens(messages) <= self.max_tokens:
            return messages

        # Separate system prompt from the rest
        system_messages = [m for m in messages if m["role"] == "system"]
        conversation = [m for m in messages if m["role"] != "system"]

        removed = 0
        while conversation and self.count_tokens(system_messages + conversation) > self.max_tokens:
            conversation.pop(0)
            removed += 1

        if removed > 0:
            logger.warning(
                f"Context trimmed: removed {removed} message(s) to stay within "
                f"{self.max_tokens} token limit."
            )

        return system_messages + conversation

    def is_over_limit(self, messages: list[dict]) -> bool:
        """Return True if the messages exceed the token limit."""
        return self.count_tokens(messages) > self.max_tokens
