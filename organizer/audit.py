"""
Audit log for Megan File Organizer.
Tracks every file move so actions can be undone.
"""

from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from core import logger
from core.constants import DATA_DIR

AUDIT_LOG_PATH = DATA_DIR / "organizer_audit.json"


class AuditLog:
    """
    JSON-based audit log.
    Each entry: {id, timestamp, src, dst, category, suggested_name, method, undone}
    """

    def __init__(self, log_path: Path = AUDIT_LOG_PATH):
        self.log_path = log_path
        self._entries: list[dict] = []
        self._load()

    def _load(self):
        if self.log_path.exists():
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    self._entries = json.load(f)
            except Exception:
                self._entries = []

    def _save(self):
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(self._entries, f, indent=2, default=str)

    def record(
        self,
        src: Path,
        dst: Path,
        category: str,
        method: str,
        suggested_name: Optional[str] = None,
    ) -> str:
        """Record a file move. Returns the entry ID."""
        entry_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self._entries):04d}"
        entry = {
            "id": entry_id,
            "timestamp": datetime.now().isoformat(),
            "src": str(src),
            "dst": str(dst),
            "category": category,
            "suggested_name": suggested_name,
            "method": method,
            "undone": False,
        }
        self._entries.append(entry)
        self._save()
        logger.info(f"Audit: {src.name} -> {dst} [{category}] [{method}]")
        return entry_id

    def undo(self, entry_id: str) -> bool:
        """Undo a specific move by ID. Moves file back to original location."""
        for entry in self._entries:
            if entry["id"] == entry_id and not entry["undone"]:
                src = Path(entry["dst"])
                dst = Path(entry["src"])
                if not src.exists():
                    logger.error(f"Undo failed: {src} no longer exists.")
                    return False
                try:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if dst.exists():
                        stem = dst.stem
                        ext = dst.suffix
                        counter = 1
                        while dst.exists():
                            dst = dst.parent / f"{stem}_restored_{counter}{ext}"
                            counter += 1
                    import shutil
                    shutil.move(str(src), str(dst))
                    entry["undone"] = True
                    self._save()
                    logger.info(f"Undo: moved {src.name} back to {dst}")
                    return True
                except Exception as e:
                    logger.error(f"Undo error: {e}")
                    return False
        return False

    def undo_last(self) -> bool:
        """Undo the most recent move."""
        for entry in reversed(self._entries):
            if not entry["undone"]:
                return self.undo(entry["id"])
        logger.info("Nothing to undo.")
        return False

    def recent(self, n: int = 10) -> list[dict]:
        """Return the n most recent audit entries."""
        return [e for e in reversed(self._entries) if not e["undone"]][:n]

    def summary(self) -> str:
        """Return a human-readable summary of recent moves."""
        recent = self.recent(5)
        if not recent:
            return "No file moves recorded yet."
        lines = [f"Last {len(recent)} moves:"]
        for e in recent:
            src_name = Path(e["src"]).name
            dst_folder = Path(e["dst"]).parent.name
            lines.append(f"  [{e['timestamp'][:16]}] {src_name!r} → {dst_folder}/ [{e['category']}]")
        return "\n".join(lines)
