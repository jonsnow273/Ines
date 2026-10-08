"""
Settings REST API routes for Megan.
Read and update application configuration.
"""

from fastapi import APIRouter

from core import config
from chatbot import list_supported

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get("/")
async def get_settings():
    """Return current application settings."""
    return {
        "model": config.default_model,
        "device": config.device,
        "quantization": config.quantization,
        "max_new_tokens": config.max_new_tokens,
        "temperature": config.temperature,
        "max_context_tokens": config.max_context_tokens,
        "default_language": config.default_language,
        "supported_languages": list_supported(),
        "confirmation_required": config.confirmation_required,
    }
