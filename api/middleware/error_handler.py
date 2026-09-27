"""
Global error handler middleware for Sephora API.
Catches unhandled exceptions and returns clean JSON errors.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from core import logger


async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler."""
    logger.error(f"Unhandled API error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
        },
    )
