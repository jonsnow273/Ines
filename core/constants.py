"""
Application-wide constants, file path resolutions, and default values for Ines.
"""

import os
from pathlib import Path

# Base Directory Resolution
CORE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CORE_DIR.parent

# Standard Directory Layout
CONFIGS_DIR = PROJECT_ROOT / "configs"
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
DOCS_DIR = PROJECT_ROOT / "docs"

# Data Subdirectories
LOGS_DIR = DATA_DIR / "logs"
CONVERSATION_HISTORY_DIR = DATA_DIR / "conversation_history"
CONVERSATIONS_DIR = CONVERSATION_HISTORY_DIR  # alias used by chatbot module
STEERING_PRESETS_DIR = DATA_DIR / "steering_presets"
ORGANIZER_DIR = DATA_DIR / "organizer"

# Default Configuration Filepaths
SETTINGS_CONFIG_PATH = CONFIGS_DIR / "ines_settings.yaml"
MODEL_CONFIG_PATH = CONFIGS_DIR / "model_config.yaml"
WHITELIST_CONFIG_PATH = CONFIGS_DIR / "automation_whitelist.yaml"
LANGUAGES_CONFIG_PATH = CONFIGS_DIR / "languages.yaml"

# Activation Steering Constants
PRESET_NEUTRAL = "neutral"
PRESET_CAUTIOUS = "cautious"
PRESET_CONCISE = "concise"
PRESET_DETAILED = "detailed"
PRESET_CREATIVE = "creative"

AVAILABLE_STEERING_PRESETS = [
    PRESET_NEUTRAL,
    PRESET_CAUTIOUS,
    PRESET_CONCISE,
    PRESET_DETAILED,
    PRESET_CREATIVE,
]

DEFAULT_STEERING_STRENGTH = 1.5
MIN_STEERING_STRENGTH = -3.0
MAX_STEERING_STRENGTH = 3.0
MAX_SAFE_STEERING_STRENGTH = 2.8

# Supported Primary Models
MODEL_MISTRAL_7B = "mistralai/Mistral-7B-Instruct-v0.3"
MODEL_GEMMA_2B = "google/gemma-2-2b-it"

# Intent Categories
INTENT_CHAT = "chat"
INTENT_AUTOMATION = "automation"

# Ensure runtime directories exist
for directory in (LOGS_DIR, CONVERSATION_HISTORY_DIR, STEERING_PRESETS_DIR, MODELS_DIR, ORGANIZER_DIR):
    os.makedirs(directory, exist_ok=True)
