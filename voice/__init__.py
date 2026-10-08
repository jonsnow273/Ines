"""
Voice module — Speech-to-text pipeline for Megan.

Provides:
- AudioRecorder: captures mic input as WAV using sounddevice
- WhisperTranscriber: local Whisper model for speech-to-text
- VoicePipeline: end-to-end listen() -> text interface

Quick usage:
    from voice import VoicePipeline

    pipeline = VoicePipeline(model_size="medium", language="en")
    pipeline.setup()
    text = pipeline.listen()
    print(f"You said: {text}")
"""

from voice.recorder import AudioRecorder
from voice.transcriber import WhisperTranscriber
from voice.pipeline import VoicePipeline

__all__ = [
    "AudioRecorder",
    "WhisperTranscriber",
    "VoicePipeline",
]
