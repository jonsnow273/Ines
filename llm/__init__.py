"""
LLM module — Local model loading and inference for Megan.

Usage:
    from llm import loader, engine
    loader.load()
    response = engine.quick_chat("Hello, Megan!")
"""

from llm.loader import ModelLoader
from llm.inference import InferenceEngine

# Global singletons used across Megan
loader = ModelLoader()
engine = InferenceEngine(loader)

__all__ = ["ModelLoader", "InferenceEngine", "loader", "engine"]
