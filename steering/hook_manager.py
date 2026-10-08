"""
TransformerLens-compatible hook manager for Megan activation steering.

Registers forward hooks on the model's residual stream layers
to intercept and modify hidden states during inference.

For models without TransformerLens (raw HuggingFace), falls back
to PyTorch native forward hooks on the transformer layers.
"""

from typing import Callable, Optional
import torch

from core import logger


class HookManager:
    """
    Manages registration and removal of forward hooks on transformer layers.

    Supports two backends:
    1. TransformerLens HookedTransformer (preferred for research)
    2. Raw HuggingFace model via PyTorch native hooks (fallback)
    """

    def __init__(self, model):
        self.model = model
        self._hooks: list = []
        self._hook_handles: list = []
        self._active_layer: Optional[int] = None
        self._backend = self._detect_backend()
        logger.info(f"HookManager initialized | backend: {self._backend}")

    def _detect_backend(self) -> str:
        """Detect whether the loaded model is a TransformerLens or HuggingFace model."""
        model_type = type(self.model).__name__
        if "HookedTransformer" in model_type:
            return "transformerlens"
        return "huggingface"

    def register_addition_hook(
        self,
        layer_index: int,
        direction_vector: torch.Tensor,
        alpha: float,
    ) -> None:
        """
        Register a forward hook that adds alpha * direction_vector
        to the residual stream at the given layer index.

        Args:
            layer_index: Which transformer layer to hook into.
            direction_vector: The steering vector (d_model,) to inject.
            alpha: Scalar multiplier controlling steering strength.
        """
        self.remove_all_hooks()
        self._active_layer = layer_index

        direction = direction_vector.clone().float()

        if self._backend == "transformerlens":
            self._register_tl_hook(layer_index, direction, alpha)
        else:
            self._register_hf_hook(layer_index, direction, alpha)

        logger.info(
            f"Steering hook registered | layer: {layer_index} | "
            f"alpha: {alpha:.2f} | vector norm: {direction.norm():.4f}"
        )

    def _register_tl_hook(self, layer_index: int, direction: torch.Tensor, alpha: float) -> None:
        """Register hook using TransformerLens hook_resid_post API."""

        def tl_hook_fn(value, hook):
            if value.device != direction.device:
                steer = direction.to(value.device)
            else:
                steer = direction
            return value + alpha * steer.to(value.dtype)

        hook_name = f"blocks.{layer_index}.hook_resid_post"
        handle = self.model.add_hook(hook_name, tl_hook_fn)
        self._hook_handles.append(handle)

    def _register_hf_hook(self, layer_index: int, direction: torch.Tensor, alpha: float) -> None:
        """Register hook using PyTorch native forward hooks on HuggingFace model layers."""
        try:
            if hasattr(self.model, "model") and hasattr(self.model.model, "layers"):
                layers = self.model.model.layers
            elif hasattr(self.model, "transformer") and hasattr(self.model.transformer, "h"):
                layers = self.model.transformer.h
            else:
                logger.warning(
                    "Could not locate transformer layers for hook injection. "
                    "Steering will be disabled for this session."
                )
                return

            actual_idx = min(layer_index, len(layers) - 1)
            target_layer = layers[actual_idx]

            def hf_hook_fn(module, input, output):
                """Add steering vector to first tensor in output tuple."""
                if isinstance(output, tuple):
                    hidden = output[0]
                    steer = direction.to(hidden.device).to(hidden.dtype)
                    steered = hidden + alpha * steer
                    return (steered,) + output[1:]
                elif isinstance(output, torch.Tensor):
                    steer = direction.to(output.device).to(output.dtype)
                    return output + alpha * steer
                return output

            handle = target_layer.register_forward_hook(hf_hook_fn)
            self._hook_handles.append(handle)

        except (IndexError, AttributeError) as e:
            logger.error(f"Failed to register HuggingFace hook at layer {layer_index}: {e}")

    def remove_all_hooks(self) -> None:
        """Remove all currently registered steering hooks."""
        if self._backend == "transformerlens":
            try:
                self.model.reset_hooks()
            except Exception:
                pass
        else:
            for handle in self._hook_handles:
                try:
                    handle.remove()
                except Exception:
                    pass

        self._hook_handles.clear()
        self._active_layer = None
        logger.debug("All steering hooks removed.")

    @property
    def is_active(self) -> bool:
        """Returns True if any steering hook is currently registered."""
        return len(self._hook_handles) > 0

    @property
    def active_layer(self) -> Optional[int]:
        return self._active_layer
