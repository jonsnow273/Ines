"""
Full voice input pipeline for Ines.
Combines AudioRecorder + WhisperTranscriber into a single
speak-and-get-text interface.
"""

import os
from typing import Optional

from core import config, logger
from voice.recorder import AudioRecorder
from voice.transcriber import WhisperTranscriber


class VoicePipeline:
    """
    End-to-end voice input pipeline.

    Usage:
        pipeline = VoicePipeline()
        pipeline.setup()
        text = pipeline.listen()   # Records mic until silence, returns text
        print(text)
    """

    def __init__(
        self,
        model_size: str = "medium",
        language: Optional[str] = None,
        use_vad: bool = True,
    ):
        self.recorder = AudioRecorder(sample_rate=16000, channels=1)
        self.transcriber = WhisperTranscriber(
            model_size=model_size,
            language=language,
        )
        self.use_vad = use_vad
        self._ready = False

    def setup(self) -> bool:
        """
        Load Whisper and verify microphone access.

        Returns:
            True if setup succeeded, False if a dependency is missing.
        """
        try:
            if not self.recorder.check_microphone():
                logger.error("No microphone found. Voice input unavailable.")
                return False

            self.transcriber.load()
            self._ready = True
            logger.info("Voice pipeline ready.")
            return True

        except Exception as e:
            logger.error(f"Voice pipeline setup failed: {e}")
            return False

    def listen(
        self,
        timeout: float = 30.0,
        fixed_duration: Optional[float] = None,
    ) -> Optional[str]:
        """
        Record audio from the microphone and return the transcribed text.

        Args:
            timeout: Maximum recording duration in seconds.
            fixed_duration: If set, record for exactly this many seconds
                            instead of using voice activity detection.

        Returns:
            Transcribed text string, or None if recording/transcription failed.
        """
        if not self._ready:
            logger.warning("Voice pipeline not set up. Call setup() first.")
            return None

        # Record
        if fixed_duration is not None:
            audio_path = self.recorder.record(duration_seconds=fixed_duration)
        elif self.use_vad:
            audio_path = self.recorder.record_until_silence(max_duration=timeout)
        else:
            audio_path = self.recorder.record(duration_seconds=timeout)

        if not audio_path:
            return None

        # Transcribe
        try:
            text = self.transcriber.transcribe(audio_path)
            return text if text else None
        finally:
            # Always clean up the temp audio file
            try:
                os.remove(audio_path)
            except Exception:
                pass

    def listen_once(self, duration: float = 5.0) -> Optional[str]:
        """Shortcut: record for exactly N seconds and transcribe."""
        return self.listen(fixed_duration=duration)

    def teardown(self) -> None:
        """Unload Whisper model and free memory."""
        self.transcriber.unload()
        self._ready = False

    @property
    def is_ready(self) -> bool:
        return self._ready
