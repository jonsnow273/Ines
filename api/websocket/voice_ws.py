"""
WebSocket handler for voice streaming.
Receives raw audio chunks from the frontend and returns transcribed text.
"""

import json
import asyncio
import tempfile
import wave
from pathlib import Path
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core import logger

router = APIRouter()

_voice_pipeline = None


def init(voice_pipeline=None):
    """Wire up voice pipeline."""
    global _voice_pipeline
    _voice_pipeline = voice_pipeline


@router.websocket("/ws/voice")
async def voice_websocket(ws: WebSocket):
    """
    WebSocket endpoint for voice input.

    Client sends binary audio frames (16kHz, mono, int16).
    Server responds with JSON:
        {"type": "transcription", "text": "..."}
        {"type": "error", "detail": "..."}
    """
    await ws.accept()
    logger.info("WebSocket voice client connected.")

    if _voice_pipeline is None or not _voice_pipeline.is_ready:
        await ws.send_json({
            "type": "error",
            "detail": "Voice pipeline not available.",
        })
        await ws.close()
        return

    try:
        while True:
            # Receive binary audio data
            audio_data = await ws.receive_bytes()

            if len(audio_data) < 100:
                continue

            # Save to temp WAV file
            tmp_path = tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False
            ).name

            try:
                with wave.open(tmp_path, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(16000)
                    wf.writeframes(audio_data)

                # Transcribe
                text = await asyncio.to_thread(
                    _voice_pipeline.transcriber.transcribe, tmp_path
                )

                if text:
                    await ws.send_json({
                        "type": "transcription",
                        "text": text,
                    })

            finally:
                Path(tmp_path).unlink(missing_ok=True)

    except WebSocketDisconnect:
        logger.info("WebSocket voice client disconnected.")
    except Exception as e:
        logger.error(f"Voice WebSocket error: {e}")
