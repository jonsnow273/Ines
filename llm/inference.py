"""
Text generation pipeline for Ines.
Handles single-turn and multi-turn generation with optional streaming.
"""

from typing import Generator, Optional

import torch

from core import config, logger
from llm.loader import ModelLoader


class InferenceEngine:
    """
    Generates text responses using the loaded local LLM.
    Supports standard (blocking) generation and token-by-token streaming.
    """

    def __init__(self, loader: ModelLoader):
        self.loader = loader

    def _ensure_loaded(self) -> None:
        """Auto-load the model if not already done."""
        if not self.loader.is_loaded:
            logger.info("Model not loaded yet. Loading now...")
            self.loader.load()

    def generate(
        self,
        messages: list[dict],
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        do_sample: Optional[bool] = None,
    ) -> str:
        """
        Generate a response for a multi-turn conversation.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts.
            max_new_tokens: Maximum tokens to generate.
            temperature: Sampling temperature (0.0 = greedy).
            do_sample: Enable/disable sampling.

        Returns:
            Generated response text as a string.
        """
        self._ensure_loaded()

        model = self.loader.model
        wrapper = self.loader.tokenizer_wrapper
        tokenizer = wrapper.tokenizer

        prompt = wrapper.apply_chat_template(messages)

        inputs = tokenizer(prompt, return_tensors="pt")

        # Move inputs to the correct device
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        _max_tokens = max_new_tokens or config.max_new_tokens
        _temperature = temperature if temperature is not None else config.temperature
        _do_sample = do_sample if do_sample is not None else (_temperature > 0.0)

        gen_kwargs = {
            "max_new_tokens": _max_tokens,
            "do_sample": _do_sample,
            "pad_token_id": wrapper.eos_token_id,
            "eos_token_id": wrapper.eos_token_id,
        }
        if _do_sample:
            gen_kwargs["temperature"] = _temperature
            gen_kwargs["top_p"] = 0.9

        logger.debug(f"Generating | tokens: {_max_tokens}, temp: {_temperature}")

        with torch.no_grad():
            output_ids = model.generate(**inputs, **gen_kwargs)

        # Decode only the newly generated tokens (exclude prompt tokens)
        input_length = inputs["input_ids"].shape[1]
        new_tokens = output_ids[0][input_length:]
        response = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

        return response

    def generate_stream(
        self,
        messages: list[dict],
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> Generator[str, None, None]:
        """
        Stream generated tokens one by one using TextIteratorStreamer.
        Suitable for WebSocket / real-time frontend token streaming.

        Args:
            messages: List of conversation messages.
            max_new_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.

        Yields:
            Individual decoded token strings as they are generated.
        """
        self._ensure_loaded()

        try:
            from transformers import TextIteratorStreamer
            import threading
        except ImportError:
            logger.warning("TextIteratorStreamer not available. Falling back to blocking generation.")
            full_response = self.generate(messages, max_new_tokens, temperature)
            for word in full_response.split():
                yield word + " "
            return

        model = self.loader.model
        wrapper = self.loader.tokenizer_wrapper
        tokenizer = wrapper.tokenizer

        prompt = wrapper.apply_chat_template(messages)
        inputs = tokenizer(prompt, return_tensors="pt")
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        _max_tokens = max_new_tokens or config.max_new_tokens
        _temperature = temperature if temperature is not None else config.temperature
        _do_sample = _temperature > 0.0

        streamer = TextIteratorStreamer(
            tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )

        gen_kwargs = {
            **inputs,
            "max_new_tokens": _max_tokens,
            "do_sample": _do_sample,
            "streamer": streamer,
            "pad_token_id": wrapper.eos_token_id,
            "eos_token_id": wrapper.eos_token_id,
        }
        if _do_sample:
            gen_kwargs["temperature"] = _temperature
            gen_kwargs["top_p"] = 0.9

        # Run generation in a background thread so we can yield from main thread
        thread = threading.Thread(target=model.generate, kwargs=gen_kwargs)
        thread.start()

        for token_text in streamer:
            yield token_text

        thread.join()

    def quick_chat(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """
        Convenience method for single-turn generation without history.

        Args:
            user_message: The user's text input.
            system_prompt: Optional system instruction override.

        Returns:
            Generated response string.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})
        return self.generate(messages)
