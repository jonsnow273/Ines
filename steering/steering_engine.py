"""
Runtime activation steering engine for Megan.

Manages the lifecycle of steering: selecting presets, computing
directions, registering hooks, and executing steered inference.
"""

import os
from pathlib import Path
from typing import Optional, Generator
import torch

from core import config, logger
from core.constants import STEERING_PRESETS_DIR, MAX_SAFE_STEERING_STRENGTH
from steering.presets import get_preset, SteeringPreset, PRESETS_REGISTRY
from steering.hook_manager import HookManager
from steering.direction_finder import DirectionFinder


class SteeringEngine:
    """
    Top-level controller for activation steering in Megan.

    Workflow:
        1. Call `calibrate()` to compute and cache all preset vectors.
        2. Call `set_preset(name, alpha)` to activate a behavioral direction.
        3. Call `generate_steered(messages)` to produce steered output.
        4. Call `reset()` to remove hooks and return to neutral behavior.
    """

    def __init__(self, model, tokenizer_wrapper, inference_engine):
        self.model = model
        self.tokenizer_wrapper = tokenizer_wrapper
        self.inference_engine = inference_engine

        self.hook_manager = HookManager(model)
        self.direction_finder = DirectionFinder(model, tokenizer_wrapper)

        self._direction_cache: dict[str, torch.Tensor] = {}
        self._active_preset: str = "neutral"
        self._active_alpha: float = 0.0

    # ------------------------------------------------------------------
    # Calibration
    # ------------------------------------------------------------------

    def calibrate(self, preset_names: Optional[list[str]] = None) -> None:
        """
        Compute and cache steering direction vectors for the given presets.
        If no names are given, calibrates all built-in presets.

        Computed vectors are saved to disk in STEERING_PRESETS_DIR
        so they only need to be computed once per model.

        Args:
            preset_names: List of preset names to calibrate. Default: all.
        """
        names = preset_names or [n for n in PRESETS_REGISTRY if n != "neutral"]
        logger.info(f"Starting calibration for presets: {names}")

        for name in names:
            cached = self._load_cached_direction(name)
            if cached is not None:
                self._direction_cache[name] = cached
                logger.info(f"Loaded cached direction for '{name}' from disk.")
                continue

            preset = get_preset(name)
            direction = self.direction_finder.compute_direction(preset)
            if direction is not None:
                self._direction_cache[name] = direction
                self._save_direction(name, direction)

        logger.info(
            f"Calibration complete. Cached directions: {list(self._direction_cache.keys())}"
        )

    def _save_direction(self, name: str, vector: torch.Tensor) -> None:
        """Save a steering vector to disk as a .pt tensor file."""
        path = STEERING_PRESETS_DIR / f"{name}.pt"
        torch.save(vector, path)
        logger.debug(f"Saved direction '{name}' to {path}")

    def _load_cached_direction(self, name: str) -> Optional[torch.Tensor]:
        """Load a previously saved steering vector from disk."""
        path = STEERING_PRESETS_DIR / f"{name}.pt"
        if path.exists():
            try:
                return torch.load(path, map_location="cpu", weights_only=True)
            except Exception as e:
                logger.warning(f"Failed to load cached direction '{name}': {e}")
        return None

    # ------------------------------------------------------------------
    # Preset Control
    # ------------------------------------------------------------------

    def set_preset(self, preset_name: str, alpha: Optional[float] = None) -> bool:
        """
        Activate a behavioral steering preset.

        Args:
            preset_name: Name of the preset ('cautious', 'concise', etc.)
            alpha: Steering strength. Uses preset default if None.
                   Clamped to MAX_SAFE_STEERING_STRENGTH automatically.

        Returns:
            True if hook was successfully registered, False otherwise.
        """
        if preset_name == "neutral":
            self.reset()
            return True

        if preset_name not in self._direction_cache:
            logger.info(f"Calibrating steering direction for '{preset_name}' on the fly...")
            self.calibrate([preset_name])
            if preset_name not in self._direction_cache:
                logger.error(f"Could not calibrate preset '{preset_name}'.")
                return False

        preset = get_preset(preset_name)
        effective_alpha = alpha if alpha is not None else preset.recommended_strength

        # Safety clamp
        if abs(effective_alpha) > MAX_SAFE_STEERING_STRENGTH:
            logger.warning(
                f"Alpha {effective_alpha:.2f} exceeds safe limit "
                f"({MAX_SAFE_STEERING_STRENGTH}). Clamping to safe value."
            )
            effective_alpha = MAX_SAFE_STEERING_STRENGTH * (1 if effective_alpha > 0 else -1)

        direction = self._direction_cache[preset_name]
        self.hook_manager.register_addition_hook(
            layer_index=preset.target_layer,
            direction_vector=direction,
            alpha=effective_alpha,
        )

        self._active_preset = preset_name
        self._active_alpha = effective_alpha

        logger.info(
            f"Active steering: '{preset_name}' | "
            f"layer: {preset.target_layer} | alpha: {effective_alpha:.2f}"
        )
        return True

    def reset(self) -> None:
        """Remove all hooks and return to neutral (unsteered) behavior."""
        self.hook_manager.remove_all_hooks()
        self._active_preset = "neutral"
        self._active_alpha = 0.0
        logger.info("Steering reset to neutral.")

    # ------------------------------------------------------------------
    # Steered Generation
    # ------------------------------------------------------------------

    def generate_steered(
        self,
        messages: list[dict],
        preset_name: Optional[str] = None,
        alpha: Optional[float] = None,
        max_new_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a response with the active or specified steering preset.

        Args:
            messages: Conversation history as list of role/content dicts.
            preset_name: Override the active preset for this call only.
            alpha: Override the steering strength for this call only.
            max_new_tokens: Token limit override.

        Returns:
            Steered response string.
        """
        if preset_name and preset_name != self._active_preset:
            self.set_preset(preset_name, alpha)
        elif alpha is not None and alpha != self._active_alpha:
            # Re-register hook with updated alpha
            self.set_preset(self._active_preset, alpha)

        response = self.inference_engine.generate(messages, max_new_tokens=max_new_tokens)
        return response

    def compare(
        self,
        messages: list[dict],
        preset_name: str,
        alpha: Optional[float] = None,
        max_new_tokens: Optional[int] = None,
    ) -> dict:
        """
        Run the same prompt through both unsteered and steered paths
        and return both outputs for side-by-side comparison.

        Args:
            messages: Conversation messages.
            preset_name: The steering preset to compare against baseline.
            alpha: Steering strength.
            max_new_tokens: Token generation limit.

        Returns:
            Dict with 'unsteered', 'steered', and 'metrics' keys.
        """
        import time

        # --- Baseline (unsteered) ---
        self.reset()
        t0 = time.time()
        unsteered = self.inference_engine.generate(messages, max_new_tokens=max_new_tokens)
        baseline_time = time.time() - t0

        # --- Steered ---
        self.set_preset(preset_name, alpha)
        t1 = time.time()
        steered = self.inference_engine.generate(messages, max_new_tokens=max_new_tokens)
        steered_time = time.time() - t1

        # Cleanup
        self.reset()

        unsteered_tokens = len(unsteered.split())
        steered_tokens = len(steered.split())

        delta_pct = round(
            ((steered_tokens - unsteered_tokens) / max(unsteered_tokens, 1)) * 100, 1
        )

        return {
            "unsteered": unsteered,
            "steered": steered,
            "preset": preset_name,
            "alpha": alpha or get_preset(preset_name).recommended_strength,
            "metrics": {
                "unsteered_tokens": unsteered_tokens,
                "steered_tokens": steered_tokens,
                "token_delta_percentage": delta_pct,
                "unsteered_latency_ms": round(baseline_time * 1000),
                "steered_latency_ms": round(steered_time * 1000),
            },
        }

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    @property
    def status(self) -> dict:
        """Return the current steering engine status."""
        return {
            "active_preset": self._active_preset,
            "active_alpha": self._active_alpha,
            "hook_active": self.hook_manager.is_active,
            "active_layer": self.hook_manager.active_layer,
            "cached_directions": list(self._direction_cache.keys()),
        }
