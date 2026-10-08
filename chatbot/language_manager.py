"""
Multilingual system prompt loader for Megan.
Reads language-specific YAML prompt files and injects them
as the system message at the start of each conversation.
"""

from pathlib import Path
from typing import Optional

from core import logger
from core.constants import PROJECT_ROOT

PROMPTS_DIR = PROJECT_ROOT / "languages" / "prompts"

# Supported language codes and their display names
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "mr": "Marathi",
}


def load_system_prompt(lang_code: str) -> str:
    """
    Load the system prompt for the given language code.
    Falls back to English if the file does not exist.

    Args:
        lang_code: ISO language code (e.g. 'hi', 'mr', 'fr').

    Returns:
        The system prompt string for that language.
    """
    lang_code = lang_code.lower().strip()
    prompt_path = PROMPTS_DIR / f"{lang_code}.yaml"

    if not prompt_path.exists():
        logger.warning(
            f"No system prompt found for language '{lang_code}'. "
            "Falling back to English."
        )
        prompt_path = PROMPTS_DIR / "en.yaml"

    try:
        try:
            import yaml
            with open(prompt_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            prompt = data.get("system_prompt", "")
        except ImportError:
            # Fallback if PyYAML not installed: read raw text after the key
            with open(prompt_path, encoding="utf-8") as f:
                content = f.read()
            lines = content.split("\n")
            prompt_lines = []
            in_prompt = False
            for line in lines:
                if line.strip().startswith("system_prompt:"):
                    in_prompt = True
                    value = line.split("system_prompt:", 1)[1].strip().strip("|").strip()
                    if value:
                        prompt_lines.append(value)
                elif in_prompt:
                    if line.startswith(" ") or line.startswith("\t"):
                        prompt_lines.append(line.strip())
                    else:
                        break
            prompt = " ".join(prompt_lines)

        if not prompt:
            raise ValueError("system_prompt field is empty")

        logger.info(f"Loaded system prompt for language: {lang_code}")
        return prompt

    except Exception as e:
        logger.error(f"Failed to load system prompt for '{lang_code}': {e}")
        return (
            "You are Megan, a helpful and safety-conscious AI assistant. "
            "Always confirm before performing irreversible actions."
        )


def is_supported(lang_code: str) -> bool:
    """Return True if the language code is in the supported list."""
    return lang_code.lower() in SUPPORTED_LANGUAGES


def list_supported() -> dict[str, str]:
    """Return the dict of supported language codes and names."""
    return SUPPORTED_LANGUAGES.copy()
