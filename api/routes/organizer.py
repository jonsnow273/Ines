"""
Organizer REST API routes for Megan.
Provides endpoints for smart autonomous file organizing, real-time watcher control,
dry-run scanning, and audit/undo management.
"""

from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from core import logger
from organizer import FolderWatcher, AuditLog

router = APIRouter(prefix="/api/organizer", tags=["File Organizer"])

_watcher: Optional[FolderWatcher] = None
_audit: Optional[AuditLog] = None


class ScanResponse(BaseModel):
    total_scanned: int
    dry_run: bool
    results: list


class UndoRequest(BaseModel):
    entry_id: Optional[str] = None


class UndoResponse(BaseModel):
    success: bool
    message: str


class OrganizerStatusResponse(BaseModel):
    is_watching: bool
    watched_dirs: List[str]
    output_dir: str
    recent_moves: list


def init(watcher: Optional[FolderWatcher] = None, audit: Optional[AuditLog] = None):
    """Wire up organizer watcher and audit log."""
    global _watcher, _audit
    _audit = audit or AuditLog()
    _watcher = watcher or FolderWatcher()


def _get_watcher() -> FolderWatcher:
    global _watcher
    if _watcher is None:
        _watcher = FolderWatcher()
    return _watcher


def _get_audit() -> AuditLog:
    global _audit
    if _audit is None:
        _audit = AuditLog()
    return _audit


@router.get("/status", response_model=OrganizerStatusResponse)
async def get_status():
    """Get current status of file organizer and watcher."""
    watcher = _get_watcher()
    audit = _get_audit()
    return OrganizerStatusResponse(
        is_watching=watcher.is_running,
        watched_dirs=[str(d) for d in watcher.watch_dirs],
        output_dir=str(watcher.mover.output_dir),
        recent_moves=audit.recent(10),
    )


@router.post("/scan", response_model=ScanResponse)
async def scan_folders(dry_run: bool = Query(default=True, description="Preview without moving")):
    """Scan watched folders and organize existing files (or dry-run)."""
    watcher = _get_watcher()
    try:
        results = watcher.scan_existing(dry_run=dry_run)
        return ScanResponse(
            total_scanned=len(results),
            dry_run=dry_run,
            results=results,
        )
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_watcher():
    """Start the real-time background folder watcher."""
    watcher = _get_watcher()
    if watcher.is_running:
        return {"status": "already_running", "message": "Watcher is already active."}
    try:
        watcher.start()
        return {"status": "started", "message": "Folder watcher started."}
    except Exception as e:
        logger.error(f"Failed to start watcher: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_watcher():
    """Stop the background folder watcher."""
    watcher = _get_watcher()
    if not watcher.is_running:
        return {"status": "not_running", "message": "Watcher is not running."}
    try:
        watcher.stop()
        return {"status": "stopped", "message": "Folder watcher stopped."}
    except Exception as e:
        logger.error(f"Failed to stop watcher: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/undo", response_model=UndoResponse)
async def undo_move(req: Optional[UndoRequest] = None):
    """Undo the last file move or a specific move by ID."""
    audit = _get_audit()
    if req and req.entry_id:
        success = audit.undo(req.entry_id)
        msg = f"Reverted move {req.entry_id}" if success else f"Failed to revert move {req.entry_id}"
    else:
        success = audit.undo_last()
        msg = "Reverted last file move" if success else "No move to revert or move target missing"

    return UndoResponse(success=success, message=msg)


@router.get("/audit")
async def get_audit_log(limit: int = Query(default=20, ge=1, le=100)):
    """Get audit log of recent file operations."""
    audit = _get_audit()
    return {
        "entries": audit.recent(limit),
        "summary": audit.summary(),
    }
