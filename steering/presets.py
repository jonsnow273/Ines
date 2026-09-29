"""
Built-in activation steering vector presets for Ines.

Each preset defines:
- Which residual stream layer to target
- What contrastive prompt pairs to extract the direction from
- Recommended steering strength (alpha)
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class SteeringPreset:
    """A single behavioral steering preset configuration."""
    name: str
    description: str
    target_layer: int
    recommended_strength: float
    max_safe_strength: float
    positive_examples: List[str]
    negative_examples: List[str]
    tags: List[str] = field(default_factory=list)


# =====================================================================
# Built-in Presets
# All contrastive prompt pairs are topic-matched to isolate only
# the behavioral axis (style) while holding semantics constant.
# =====================================================================

PRESET_NEUTRAL = SteeringPreset(
    name="neutral",
    description="Standard unsteered output. Model behaves according to its base training.",
    target_layer=0,
    recommended_strength=0.0,
    max_safe_strength=0.0,
    positive_examples=[],
    negative_examples=[],
    tags=["default", "baseline"],
)

PRESET_CAUTIOUS = SteeringPreset(
    name="cautious",
    description=(
        "Raises the model's risk awareness and safety scrutiny. "
        "Increases hedging, requests verification before irreversible actions, "
        "and surfaces potential downsides before acting."
    ),
    target_layer=16,
    recommended_strength=2.0,
    max_safe_strength=2.8,
    positive_examples=[
        "Before deleting those files, I want to make sure you have a backup. "
        "This action cannot be undone. Are you certain?",
        "I would strongly recommend verifying this before proceeding. "
        "There are several risks to consider here.",
        "Warning: this operation will permanently overwrite the existing data. "
        "Please confirm you want to continue.",
    ],
    negative_examples=[
        "Sure, deleting all files now!",
        "Done! I removed everything as requested.",
        "No problem, I will proceed immediately.",
    ],
    tags=["safety", "automation", "risk"],
)

PRESET_CONCISE = SteeringPreset(
    name="concise",
    description=(
        "Produces short, direct, no-filler responses. "
        "Removes conversational preambles, pleasantries, and redundant elaboration. "
        "Average 60-70 percent reduction in output token count."
    ),
    target_layer=19,
    recommended_strength=1.8,
    max_safe_strength=2.5,
    positive_examples=[
        "Virtual memory maps disk to RAM addresses for process isolation.",
        "TCP: reliable, ordered delivery. UDP: fast, connectionless, lossy.",
        "Use `git rebase` to linearize history. `git merge` preserves branch topology.",
    ],
    negative_examples=[
        "Great question! Virtual memory is a fascinating topic in computer science. "
        "Let me explain it step by step for you...",
        "Of course! I would be happy to help you understand the difference between TCP and UDP. "
        "These are two fundamental networking protocols...",
        "Certainly! Both git rebase and git merge are important tools. "
        "Let me walk you through each one in detail...",
    ],
    tags=["brevity", "cli", "voice", "speed"],
)

PRESET_DETAILED = SteeringPreset(
    name="detailed",
    description=(
        "Encourages structured, step-by-step explanations with technical depth. "
        "Produces enumerated reasoning, edge cases, and comprehensive coverage."
    ),
    target_layer=21,
    recommended_strength=1.6,
    max_safe_strength=2.5,
    positive_examples=[
        "Let me walk through this step by step. First, consider the following edge cases: "
        "1) What happens if the input is empty? 2) What if the file is locked by another process? "
        "3) How does this behave on Windows vs Linux?",
        "There are several important considerations here. To fully understand this, "
        "we need to examine the underlying mechanism, its performance characteristics, "
        "failure modes, and best practices for production use.",
    ],
    negative_examples=[
        "It works by caching data.",
        "Just use a list.",
        "It depends on your use case.",
    ],
    tags=["depth", "code", "explanation", "debugging"],
)

PRESET_CREATIVE = SteeringPreset(
    name="creative",
    description=(
        "Increases semantic diversity and novel token associations. "
        "Produces more imaginative, non-obvious suggestions without "
        "increasing sampling temperature (avoiding gibberish)."
    ),
    target_layer=13,
    recommended_strength=1.4,
    max_safe_strength=2.2,
    positive_examples=[
        "Imagine the data as a river of light, where each packet is a photon "
        "carrying its message across a sea of fiber optic pathways.",
        "What if the cache was not a storage layer but a conversation "
        "between the CPU and RAM, each one finishing the other's sentences?",
    ],
    negative_examples=[
        "The cache stores frequently accessed data.",
        "Packets are units of data transmitted over a network.",
    ],
    tags=["creativity", "brainstorm", "writing", "design"],
)


# Registry: name -> preset
PRESETS_REGISTRY: dict[str, SteeringPreset] = {
    p.name: p for p in [
        PRESET_NEUTRAL,
        PRESET_CAUTIOUS,
        PRESET_CONCISE,
        PRESET_DETAILED,
        PRESET_CREATIVE,
    ]
}


def get_preset(name: str) -> SteeringPreset:
    """
    Retrieve a preset by name.
    Falls back to neutral if the name is not found.
    """
    return PRESETS_REGISTRY.get(name.lower(), PRESET_NEUTRAL)


def list_presets() -> list[str]:
    """Return names of all available presets."""
    return list(PRESETS_REGISTRY.keys())
