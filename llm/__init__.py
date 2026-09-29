"""
LLM module — Local model loading and inference for Ines.

Usage:
    from llm import loader, engine
    loader.load()
    response = engine.quick_chat("Hello, Ines!")
"""

from llm.loader import ModelLoader
from llm.inference import InferenceEngine

# Global singletons used across Ines
loader = ModelLoader()
engine = InferenceEngine(loader)

__all__ = ["ModelLoader", "InferenceEngine", "loader", "engine"]
