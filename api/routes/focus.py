"""
FastAPI REST routes for Megan Focus & Anti-Distraction Coach.
Allows the React dashboard to start/stop focus sessions, inspect live
analytics, configure thresholds, and trigger one-click workspace restoration.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from core import logger
from focus.coach import FocusCoach
from focus.tracker import FocusTracker

router = APIRouter(prefix="/api/focus", tags=["Focus Coach"])

# Global singleton FocusCoach
_coach = FocusCoach()


def init(coach: Optional[FocusCoach] = None):
    """Inject or configure coach singleton."""
    global _coach
    _coach = coach or FocusCoach()
    logger.info("Focus routes initialized.")


# ── Request / Response Models ─────────────────────────────────

class StartFocusRequest(BaseModel):
    goal: str = Field(default="Deep Work", description="Goal of the focus session")
    duration_minutes: int = Field(default=45, ge=5, le=360, description="Duration in minutes")


class RestoreRequest(BaseModel):
    target_app: Optional[str] = Field(default=None, description="Process name to restore (e.g. 'code', 'windowsterminal')")


# ── Endpoints ─────────────────────────────────────────────────

@router.get("/status")
async def get_focus_status():
    """Retrieve live focus session telemetry and productivity analytics."""
    return _coach.status()


@router.post("/start")
async def start_focus_session(req: StartFocusRequest):
    """Start an active focus session with automated distraction monitoring."""
    _coach.start_session(goal=req.goal, duration_minutes=req.duration_minutes)
    return {
        "message": f"Focus session '{req.goal}' started for {req.duration_minutes} minutes.",
        "status": _coach.status(),
    }


@router.post("/stop")
async def stop_focus_session():
    """Stop the current focus session and retrieve summary scorecard."""
    summary = _coach.stop_session()
    return {
        "message": "Focus session ended.",
        "summary": summary,
    }


@router.post("/restore")
async def restore_workspace(req: RestoreRequest):
    """
    One-click workspace restoration:
    Brings target development window (VS Code or Terminal) to the foreground.
    """
    success = _coach.restore_workspace(target_proc=req.target_app)
    if not success:
        return {
            "success": False,
            "message": f"Could not find or focus window for '{req.target_app or _coach.target_app}'. Is it open?",
        }
    return {
        "success": True,
        "message": f"Restored workspace window for '{req.target_app or _coach.target_app}'!",
    }


@router.get("/categories")
async def get_app_categories():
    """Return categorized list of productive vs distracting rules."""
    return _coach.tracker.config.get("categories", {})
