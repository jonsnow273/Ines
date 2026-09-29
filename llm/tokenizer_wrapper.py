"""
Tokenizer abstraction layer for Ines.
Handles prompt formatting and chat template application.
"""

from typing import Any


class TokenizerWrapper:
    """
    Wraps a HuggingFace tokenizer to provide clean prompt formatting
    and chat template utilities for both Mistral and Gemma models.
    """

    def __init__(self, tokenizer: Any, model_name: str):
        self.tokenizer = tokenizer
        self.model_name = model_name.lower()

        # Set padding token if missing (required for batched inference)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def apply_chat_template(self, messages: list[dict]) -> str:
        """
        Apply the model's chat template to a list of messages.
        Falls back to a simple manual format if the tokenizer
        doesn't have a built-in chat template.

        Args:
            messages: List of {"role": "user"/"assistant"/"system", "content": "..."}

        Returns:
            Formatted string prompt ready for tokenization.
        """
        try:
            return self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            return self._manual_format(messages)

    def _manual_format(self, messages: list[dict]) -> str:
        """Fallback formatter for models without a built-in chat template."""
        result = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                result += f"<|system|>\n{content}\n"
            elif role == "user":
                result += f"<|user|>\n{content}\n"
            elif role == "assistant":
                result += f"<|assistant|>\n{content}\n"
        result += "<|assistant|>\n"
        return result

    def encode(self, text: str, **kwargs) -> Any:
        """Tokenize text and return input tensors."""
        return self.tokenizer(text, return_tensors="pt", **kwargs)

    @property
    def eos_token_id(self) -> int:
        return self.tokenizer.eos_token_id

    @property
    def vocab_size(self) -> int:
        return self.tokenizer.vocab_size
