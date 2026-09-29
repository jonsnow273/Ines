"""
Whisper speech-to-text transcriber for Ines.
Loads OpenAI Whisper locally and transcribes audio files to text.
"""

import os
from pathlib import Path
from typing import Optional

from core import config, logger


class WhisperTranscriber:
    """
    Wraps OpenAI Whisper for local speech-to-text transcription.
    Supports auto language detection and explicit language codes.

    Model sizes (accuracy vs speed):
        tiny   — fastest, lowest accuracy (~39 MB)
        base   — good balance for English (~74 MB)
        small  — better multilingual (~244 MB)
        medium — strong multilingual accuracy (~769 MB) ← default
        large  — best quality (~1.5 GB)
    """

    def __init__(self, model_size: str = "medium", language: Optional[str] = None):
        self.model_size = model_size
        self.language = language  # None = auto-detect
        self._model = None

    def load(self) -> None:
        """Load the Whisper model into memory."""
        if self._model is not None:
            return
        try:
            import whisper
            logger.info(f"Loading Whisper model: {self.model_size}")
            self._model = whisper.load_model(self.model_size)
            logger.info(f"Whisper {self.model_size} loaded.")
        except ImportError:
            logger.error(
                "openai-whisper not installed. Run: pip install openai-whisper"
            )
            raise

    def transcribe(self, audio_path: str) -> Optional[str]:
        """
        Transcribe a WAV or MP3 file to text.

        Args:
            audio_path: Path to the audio file.

        Returns:
            Transcribed text string, or None on failure.
        """
        if self._model is None:
            self.load()

        if not Path(audio_path).exists():
            logger.error(f"Audio file not found: {audio_path}")
            return None

        try:
            logger.debug(f"Transcribing: {audio_path}")
            options = {}
            if self.language:
                options["language"] = self.language

            result = self._model.transcribe(audio_path, **options)
            text = result.get("text", "").strip()

            detected_lang = result.get("language", "unknown")
            logger.info(f"Transcribed [{detected_lang}]: {text[:80]}{'...' if len(text) > 80 else ''}")

            return self._clean(text)

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None

    def _clean(self, text: str) -> str:
        """
        Basic post-processing to clean up Whisper output.
        Removes common filler artifacts from raw transcription.
        """
        # Strip leading/trailing whitespace
        text = text.strip()

        # Whisper sometimes outputs these when audio is silent
        filler_artifacts = [
            "Thank you.", "Thanks for watching.", "Thank you for watching.",
            "[BLANK_AUDIO]", "(silence)", "...", "you",
        ]
        for artifact in filler_artifacts:
            if text.strip().lower() == artifact.lower():
                return ""

        return text

    def unload(self) -> None:
        """Free the Whisper model from memory."""
        if self._model is not None:
            del self._model
            self._model = None
            logger.info("Whisper model unloaded.")

    @property
    def is_loaded(self) -> bool:
        return self._model is not None
