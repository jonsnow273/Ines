"""
Voice REST API routes for Ines.
Provides voice pipeline status and configuration.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/voice", tags=["Voice"])

_voice_pipeline = None


def init(voice_pipeline=None):
    """Wire up voice pipeline."""
    global _voice_pipeline
    _voice_pipeline = voice_pipeline


@router.get("/status")
async def voice_status():
    """Check voice pipeline readiness."""
    if _voice_pipeline is None:
        return {"available": False, "message": "Voice pipeline not initialized."}
    return {
        "available": True,
        "ready": _voice_pipeline.is_ready,
        "model_size": _voice_pipeline.transcriber.model_size,
        "model_loaded": _voice_pipeline.transcriber.is_loaded,
    }
