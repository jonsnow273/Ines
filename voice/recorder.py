"""
Microphone recorder for Ines.
Captures audio from the default input device and saves it as a WAV file.
Uses sounddevice for cross-platform mic access.
"""

import wave
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np

from core import config, logger


class AudioRecorder:
    """
    Records audio from the system microphone.
    Produces a temporary WAV file ready for Whisper transcription.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        dtype: str = "int16",
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype

    def record(self, duration_seconds: float) -> Optional[str]:
        """
        Record audio for a fixed duration.

        Args:
            duration_seconds: How many seconds to record.

        Returns:
            Path to the saved temporary WAV file, or None on failure.
        """
        try:
            import sounddevice as sd
        except ImportError:
            logger.error(
                "sounddevice not installed. Run: pip install sounddevice"
            )
            return None

        logger.info(f"Recording for {duration_seconds:.1f}s...")
        try:
            frames = sd.rec(
                int(duration_seconds * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
            )
            sd.wait()
            logger.info("Recording complete.")
            return self._save_wav(frames)
        except Exception as e:
            logger.error(f"Recording failed: {e}")
            return None

    def record_until_silence(
        self,
        silence_threshold: float = 0.01,
        silence_duration: float = 1.5,
        max_duration: float = 30.0,
        chunk_size: int = 1024,
    ) -> Optional[str]:
        """
        Record until the user stops speaking (voice activity detection).

        Args:
            silence_threshold: RMS amplitude below which audio is considered silence.
            silence_duration: Seconds of silence before stopping.
            max_duration: Hard cap on recording length.
            chunk_size: Number of frames per audio chunk.

        Returns:
            Path to the saved temporary WAV file, or None on failure.
        """
        try:
            import sounddevice as sd
        except ImportError:
            logger.error("sounddevice not installed. Run: pip install sounddevice")
            return None

        logger.info("Listening... (speak now)")
        frames_all = []
        silent_chunks = 0
        silence_limit = int(silence_duration * self.sample_rate / chunk_size)
        max_chunks = int(max_duration * self.sample_rate / chunk_size)

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
            ) as stream:
                for _ in range(max_chunks):
                    chunk, _ = stream.read(chunk_size)
                    frames_all.append(chunk.copy())

                    rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
                    if rms < silence_threshold * 32768:
                        silent_chunks += 1
                    else:
                        silent_chunks = 0

                    if silent_chunks >= silence_limit and len(frames_all) > silence_limit:
                        break

            logger.info(f"Captured {len(frames_all) * chunk_size / self.sample_rate:.1f}s of audio.")
            audio = np.concatenate(frames_all, axis=0)
            return self._save_wav(audio)

        except Exception as e:
            logger.error(f"VAD recording failed: {e}")
            return None

    def _save_wav(self, audio_array: np.ndarray) -> str:
        """Save a numpy audio array to a temporary WAV file."""
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_path = tmp.name
        tmp.close()

        with wave.open(tmp_path, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # int16 = 2 bytes
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_array.tobytes())

        logger.debug(f"Audio saved: {tmp_path}")
        return tmp_path

    def check_microphone(self) -> bool:
        """Quick test to verify that a microphone is accessible."""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            input_devices = [d for d in devices if d["max_input_channels"] > 0]
            if input_devices:
                logger.info(f"Microphone available: {input_devices[0]['name']}")
                return True
            logger.warning("No input devices found.")
            return False
        except Exception as e:
            logger.error(f"Microphone check failed: {e}")
            return False
