"""
Core foundation module for Megan.
Provides centralized constants, logger, and configuration instances.
"""

from core.constants import (
    PROJECT_ROOT,
    CONFIGS_DIR,
    DATA_DIR,
    LOGS_DIR,
    AVAILABLE_STEERING_PRESETS,
    PRESET_NEUTRAL,
    PRESET_CAUTIOUS,
    PRESET_CONCISE,
    PRESET_DETAILED,
    PRESET_CREATIVE,
)
from core.logger import logger
from core.config import config

__all__ = [
    "PROJECT_ROOT",
    "CONFIGS_DIR",
    "DATA_DIR",
    "LOGS_DIR",
    "AVAILABLE_STEERING_PRESETS",
    "PRESET_NEUTRAL",
    "PRESET_CAUTIOUS",
    "PRESET_CONCISE",
    "PRESET_DETAILED",
    "PRESET_CREATIVE",
    "logger",
    "config",
]
