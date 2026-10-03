"""
Ines File Organizer — Autonomous Smart File Organization Module.

Watches your Downloads, Desktop, and Documents folders in real-time,
classifies each new file using extension rules and local LLM intelligence,
and automatically moves it to a clean organized folder structure.

Features:
- Real-time folder watching (watchdog)
- Extension-based fast classification (instant, no LLM)
- LLM deep classification for ambiguous files (txt, csv, md, json)
- Smart file renaming using local LLM
- Duplicate detection (skip identical files)
- Full audit trail with undo support
- Confirmation gate for safety

Usage:
    from organizer import FolderWatcher, FileClassifier, AuditLog

    # Start watching in background
    watcher = FolderWatcher()
    watcher.start()

    # One-shot scan of existing files
    results = watcher.scan_existing(dry_run=True)

    # Undo last move
    from organizer import AuditLog
    audit = AuditLog()
    audit.undo_last()
"""

from organizer.classifier import FileClassifier, ClassificationResult
from organizer.watcher import FolderWatcher
from organizer.mover import FileMover
from organizer.audit import AuditLog
from organizer.rules import (
    classify_by_extension,
    CATEGORY_FOLDERS,
    EXTENSION_MAP,
    BLACKLIST_EXTENSIONS,
)

__all__ = [
    "FileClassifier",
    "ClassificationResult",
    "FolderWatcher",
    "FileMover",
    "AuditLog",
    "classify_by_extension",
    "CATEGORY_FOLDERS",
    "EXTENSION_MAP",
    "BLACKLIST_EXTENSIONS",
]
