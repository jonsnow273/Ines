"""
File Mover for Megan File Organizer.
Safely moves files to organized folders with confirmation, dedup, and audit trail.
"""

from __future__ import annotations
import shutil
from pathlib import Path
from typing import Optional

from core import logger, config
from organizer.classifier import ClassificationResult
from organizer.audit import AuditLog


class FileMover:
    """
    Moves classified files to organized output directory.
    Features:
    - Configurable output base directory
    - Duplicate detection (skips if identical file exists)
    - Auto-numbering for name conflicts (file.pdf → file_2.pdf)
    - Full audit trail for undo
    - Confirmation gate for any move (configurable)
    """

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        require_confirmation: bool = False,
        audit: Optional[AuditLog] = None,
    ):
        self.output_dir = Path(output_dir) if output_dir else self._default_output()
        self.require_confirmation = require_confirmation
        self.audit = audit or AuditLog()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _default_output(self) -> Path:
        """Default organized folder: user home / Organized."""
        return Path.home() / "Organized"

    def _resolve_destination(self, result: ClassificationResult) -> Path:
        """Build destination path, resolving name conflicts."""
        dest_dir = self.output_dir / result.target_folder
        dest_dir.mkdir(parents=True, exist_ok=True)

        filename = result.final_name
        dest = dest_dir / filename

        # Handle name conflicts with auto-numbering
        if dest.exists():
            # Check if it's the same file (dedup)
            if self._is_duplicate(result.filepath, dest):
                return dest  # Will be skipped
            # Different file, add suffix
            stem = Path(filename).stem
            ext = Path(filename).suffix
            counter = 2
            while dest.exists():
                dest = dest_dir / f"{stem}_{counter}{ext}"
                counter += 1

        return dest

    def _is_duplicate(self, src: Path, dst: Path) -> bool:
        """Check if src and dst are identical files (by size + first 4KB)."""
        try:
            if src.stat().st_size != dst.stat().st_size:
                return False
            with open(src, "rb") as f1, open(dst, "rb") as f2:
                return f1.read(4096) == f2.read(4096)
        except Exception:
            return False

    def move(self, result: ClassificationResult) -> dict:
        """
        Move a classified file to its organized destination.
        Returns result dict with: success, src, dst, action
        """
        if result.skip:
            return {"success": False, "action": "skipped", "reason": result.skip_reason}

        src = result.filepath
        if not src.exists():
            return {"success": False, "action": "skipped", "reason": "file not found"}

        dest = self._resolve_destination(result)

        # Duplicate check
        if dest.exists() and self._is_duplicate(src, dest):
            logger.info(f"Duplicate: {src.name} already exists at {dest}. Skipping.")
            return {"success": True, "action": "duplicate_skipped", "src": str(src), "dst": str(dest)}

        # Confirmation gate
        if self.require_confirmation:
            return {
                "success": False,
                "action": "pending_confirmation",
                "src": str(src),
                "dst": str(dest),
                "category": result.category,
            }

        # Execute move
        try:
            shutil.move(str(src), str(dest))
            self.audit.record(
                src=src,
                dst=dest,
                category=result.category,
                method=result.method,
                suggested_name=result.suggested_name,
            )
            logger.info(f"Moved: {src.name!r} -> {dest}")
            return {"success": True, "action": "moved", "src": str(src), "dst": str(dest)}
        except Exception as e:
            logger.error(f"Move failed for {src.name!r}: {e}")
            return {"success": False, "action": "error", "reason": str(e)}
