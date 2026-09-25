"""
Centralized configuration manager for Sephora.
Loads environment variables from .env and YAML configurations from configs/.
Features graceful fallbacks if pyyaml or python-dotenv are not yet installed.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from core.constants import (
    PROJECT_ROOT,
    SETTINGS_CONFIG_PATH,
    MODEL_CONFIG_PATH,
    WHITELIST_CONFIG_PATH,
    LANGUAGES_CONFIG_PATH,
)

# Optional dependency: python-dotenv
try:
    from dotenv import load_dotenv
    ENV_PATH = PROJECT_ROOT / ".env"
    load_dotenv(dotenv_path=ENV_PATH)
except ImportError:
    pass

# Optional dependency: pyyaml
try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


class ConfigManager:
    """Singleton configuration manager combining YAML settings and environment variables."""

    def __init__(self):
        self._settings: Dict[str, Any] = {}
        self._model_config: Dict[str, Any] = {}
        self._whitelist: Dict[str, Any] = {}
        self._languages: Dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        """Reload all configuration files from disk."""
        self._settings = self._load_yaml(SETTINGS_CONFIG_PATH)
        self._model_config = self._load_yaml(MODEL_CONFIG_PATH)
        self._whitelist = self._load_yaml(WHITELIST_CONFIG_PATH)
        self._languages = self._load_yaml(LANGUAGES_CONFIG_PATH)

    @staticmethod
    def _load_yaml(path: Path) -> Dict[str, Any]:
        """Safely load a YAML file, returning an empty dict if missing or unparseable."""
        if not path.exists() or not _YAML_AVAILABLE:
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                return content if isinstance(content, dict) else {}
        except Exception:
            return {}

    # Dot-notation / Key Lookup
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Retrieve nested config values using dot-notation.
        Example: config.get("steering.default_preset", "neutral")
        """
        parts = key_path.split(".")
        current = self._settings

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current if current is not None else default

    # Typed Properties for major subsystems
    @property
    def assistant_name(self) -> str:
        return self.get("assistant.name", "Sephora")

    @property
    def default_language(self) -> str:
        return self.get("assistant.default_language", "en")

    # Steering settings
    @property
    def steering_enabled(self) -> bool:
        return bool(self.get("steering.enabled", True))

    @property
    def default_steering_preset(self) -> str:
        return str(self.get("steering.default_preset", "neutral"))

    @property
    def default_steering_strength(self) -> float:
        return float(self.get("steering.default_strength", 1.5))

    @property
    def max_safe_steering_strength(self) -> float:
        return float(self.get("steering.max_safe_strength", 2.8))

    @property
    def default_target_layer(self) -> int:
        return int(self.get("steering.target_layer_default", 16))

    # LLM settings
    @property
    def model_name(self) -> str:
        return str(self.get("llm.model_name", "Qwen/Qwen2.5-0.5B-Instruct"))

    @property
    def alternate_model_name(self) -> str:
        return str(self.get("llm.alternate_model", "mistralai/Mistral-7B-Instruct-v0.3"))

    @property
    def device(self) -> str:
        env_device = os.getenv("SEPHORA_DEVICE")
        if env_device:
            return env_device.lower()
        return str(self.get("llm.device", "cuda"))

    @property
    def quantization(self) -> str:
        return str(self.get("llm.quantization", "4bit"))

    @property
    def max_new_tokens(self) -> int:
        return int(self.get("llm.max_new_tokens", 512))

    @property
    def temperature(self) -> float:
        return float(self.get("llm.temperature", 0.7))

    @property
    def max_context_tokens(self) -> int:
        return int(self.get("llm.max_context_tokens", 3500))

    @property
    def default_language(self) -> str:
        return str(self.get("assistant.default_language", "en"))

    # Automation settings
    @property
    def confirmation_required(self) -> bool:
        return bool(self.get("automation.confirmation_required", True))

    @property
    def safe_delete(self) -> bool:
        return bool(self.get("automation.safe_delete", True))

    @property
    def sandbox_mode(self) -> bool:
        return bool(self.get("automation.sandbox_mode", False))

    @property
    def whitelisted_actions(self) -> Dict[str, Any]:
        return self._whitelist.get("actions", {})

    @property
    def destructive_actions(self) -> list:
        return self._whitelist.get("destructive_actions", [])

    # Voice settings
    @property
    def voice_enabled(self) -> bool:
        return bool(self.get("voice.enabled", True))

    @property
    def wake_phrase(self) -> str:
        return str(self.get("assistant.wake_phrase", "hey sephora"))

    # Environment overrides
    @property
    def hf_token(self) -> Optional[str]:
        return os.getenv("HF_TOKEN")


# Global Configuration Singleton Instance
config = ConfigManager()
