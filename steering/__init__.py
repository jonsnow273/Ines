"""
Steering module — Activation Steering research core for Megan.

Provides:
- SteeringPreset definitions and registry (presets.py)
- TransformerLens-compatible hook manager (hook_manager.py)
- Contrastive activation vector extraction (direction_finder.py)
- High-level steering engine with compare() API (steering_engine.py)

Quick usage after model is loaded:
    from steering import SteeringEngine
    from llm import loader, engine as inference_engine

    se = SteeringEngine(loader.model, loader.tokenizer_wrapper, inference_engine)
    se.calibrate(["concise", "cautious"])
    se.set_preset("concise", alpha=1.8)
    response = se.generate_steered(messages)
    result = se.compare(messages, preset_name="cautious")
"""

from steering.presets import (
    SteeringPreset,
    get_preset,
    list_presets,
    PRESETS_REGISTRY,
    PRESET_NEUTRAL,
    PRESET_CAUTIOUS,
    PRESET_CONCISE,
    PRESET_DETAILED,
    PRESET_CREATIVE,
)
from steering.hook_manager import HookManager
from steering.direction_finder import DirectionFinder
from steering.steering_engine import SteeringEngine

__all__ = [
    "SteeringPreset",
    "get_preset",
    "list_presets",
    "PRESETS_REGISTRY",
    "PRESET_NEUTRAL",
    "PRESET_CAUTIOUS",
    "PRESET_CONCISE",
    "PRESET_DETAILED",
    "PRESET_CREATIVE",
    "HookManager",
    "DirectionFinder",
    "SteeringEngine",
]
