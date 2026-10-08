"""
FastAPI REST routes for Megan Digital Memory.
Allows the React frontend dashboard and external clients to control capture,
search screen history, retrieve screenshots, and manage privacy settings.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core import logger
from auth.models import User
from auth.middleware import get_current_user
from memory.service import DigitalMemoryService

router = APIRouter(prefix="/api/memory", tags=["Digital Memory"])

# Singleton default service instance
_memory_service: Optional[DigitalMemoryService] = None


def init(memory_service: Optional[DigitalMemoryService] = None):
    """Initialize or inject the memory service singleton."""
    global _memory_service
    _memory_service = memory_service or DigitalMemoryService()
    logger.info("Memory routes initialized.")


def get_service(user: Optional[User] = Depends(get_current_user)) -> DigitalMemoryService:
    """Dependency that returns user-scoped memory service or global fallback."""
    global _memory_service
    if user:
        return DigitalMemoryService.for_user(user.username)
    if _memory_service is None:
        _memory_service = DigitalMemoryService()
    return _memory_service


# ── Request / Response Models ─────────────────────────────────

class PauseRequest(BaseModel):
    minutes: int = Field(default=15, ge=1, le=1440, description="Minutes to pause memory capture")


class SearchResult(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    score: float


class PrivacyConfigRequest(BaseModel):
    enabled: bool = True
    blacklisted_processes: List[str] = []
    blacklisted_window_titles: List[str] = []


# ── Endpoints ─────────────────────────────────────────────────

@router.get("/status")
async def get_status(service: DigitalMemoryService = Depends(get_service)):
    """Retrieve runtime status and telemetry for Digital Memory."""
    return service.status()


@router.post("/start")
async def start_memory(service: DigitalMemoryService = Depends(get_service)):
    """Start the background memory capture engine."""
    success = service.start()
    return {"message": "Digital Memory daemon started", "running": service.is_running}


@router.post("/stop")
async def stop_memory(service: DigitalMemoryService = Depends(get_service)):
    """Stop the background memory capture engine."""
    success = service.stop()
    return {"message": "Digital Memory daemon stopped", "running": service.is_running}


@router.post("/pause")
async def pause_memory(req: PauseRequest, service: DigitalMemoryService = Depends(get_service)):
    """Temporarily pause memory capture for privacy."""
    service.pause(minutes=req.minutes)
    return {"message": f"Digital Memory paused for {req.minutes} minutes", "paused": True}


@router.post("/resume")
async def resume_memory(service: DigitalMemoryService = Depends(get_service)):
    """Resume memory capture from pause."""
    service.resume()
    return {"message": "Digital Memory resumed", "paused": False}


@router.post("/capture-now")
async def capture_now(service: DigitalMemoryService = Depends(get_service)):
    """Manually trigger a single screen capture immediately."""
    result = service.process_frame(force=True)
    return result


@router.get("/search", response_model=List[SearchResult])
async def search_memory(
    q: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(5, ge=1, le=50, description="Max results to return"),
    service: DigitalMemoryService = Depends(get_service),
):
    """
    Search past digital memory using semantic vector similarity.
    Returns ranked screenshot matches with OCR text and timestamp metadata.
    """
    results = service.search(query=q, top_k=limit)
    return results


@router.get("/screenshot/{filename}")
async def get_screenshot(
    filename: str,
    service: DigitalMemoryService = Depends(get_service),
):
    """Retrieve the JPEG image file for a specific screenshot."""
    # Sanitize filename
    safe_filename = Path(filename).name
    image_path = service.screenshots_dir / safe_filename

    if not image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screenshot '{safe_filename}' not found",
        )

    return FileResponse(image_path, media_type="image/jpeg")


@router.get("/privacy")
async def get_privacy_settings(service: DigitalMemoryService = Depends(get_service)):
    """Get the active privacy blacklist settings."""
    return {
        "enabled": service.privacy.enabled,
        "blacklisted_processes": service.privacy.blacklisted_processes,
        "blacklisted_window_titles": service.privacy.blacklisted_window_titles,
    }
