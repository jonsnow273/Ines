"""
Real-time Folder Watcher for Megan File Organizer.
Uses watchdog to monitor folders and trigger classification + move on new files.
"""

from __future__ import annotations
import threading
import time
from pathlib import Path
from typing import Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from core import logger
from organizer.classifier import FileClassifier
from organizer.mover import FileMover

# Seconds to wait after file creation before processing
# (handles partial downloads / in-progress writes)
SETTLE_DELAY = 3.0


class NewFileHandler(FileSystemEventHandler):
    """Handles new file creation events from watchdog."""

    def __init__(self, classifier: FileClassifier, mover: FileMover, callback=None):
        super().__init__()
        self.classifier = classifier
        self.mover = mover
        self.callback = callback  # Optional: called with move result
        self._pending: dict[str, threading.Timer] = {}

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        # Cancel existing timer for this file (handles rapid re-creates)
        if str(path) in self._pending:
            self._pending[str(path)].cancel()
        # Schedule processing after settle delay
        timer = threading.Timer(SETTLE_DELAY, self._process, args=[path])
        self._pending[str(path)] = timer
        timer.start()

    def _process(self, filepath: Path):
        """Classify and move a newly detected file."""
        self._pending.pop(str(filepath), None)

        if not filepath.exists():
            return  # File disappeared (temp file, etc.)

        logger.info(f"Watcher: new file detected -> {filepath.name}")

        result = self.classifier.classify(filepath)

        if result.skip:
            logger.debug(f"Watcher: skipping {filepath.name!r} ({result.skip_reason})")
            return

        move_result = self.mover.move(result)

        if self.callback:
            try:
                self.callback(filepath, result, move_result)
            except Exception as e:
                logger.error(f"Watcher callback error: {e}")


class FolderWatcher:
    """
    Watches one or more directories for new files and auto-organizes them.
    Runs in a background daemon thread.
    """

    def __init__(
        self,
        watch_dirs: Optional[list[Path]] = None,
        output_dir: Optional[Path] = None,
        require_confirmation: bool = False,
        use_llm: bool = True,
        callback=None,
    ):
        self.watch_dirs = watch_dirs or self._default_watch_dirs()
        self.classifier = FileClassifier(use_llm=use_llm)
        self.mover = FileMover(
            output_dir=output_dir,
            require_confirmation=require_confirmation,
        )
        self.callback = callback
        self._observer: Optional[Observer] = None
        self._running = False

    def _default_watch_dirs(self) -> list[Path]:
        """Watch Downloads and Desktop by default."""
        home = Path.home()
        candidates = [
            home / "Downloads",
            home / "Desktop",
        ]
        return [d for d in candidates if d.exists()]

    def start(self):
        """Start watching all configured directories."""
        if self._running:
            logger.warning("FolderWatcher already running.")
            return

        handler = NewFileHandler(self.classifier, self.mover, self.callback)
        self._observer = Observer()

        for watch_dir in self.watch_dirs:
            if watch_dir.exists():
                self._observer.schedule(handler, str(watch_dir), recursive=False)
                logger.info(f"FolderWatcher: watching {watch_dir}")
            else:
                logger.warning(f"FolderWatcher: {watch_dir} does not exist, skipping.")

        self._observer.start()
        self._running = True
        logger.info(f"FolderWatcher started. Watching {len(self.watch_dirs)} folder(s).")

    def stop(self):
        """Stop the watcher."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._running = False
            logger.info("FolderWatcher stopped.")

    @property
    def is_running(self) -> bool:
        return self._running

    def scan_existing(self, dry_run: bool = False) -> list[dict]:
        """
        One-shot scan: classify and move all existing files in watched folders.
        Set dry_run=True to see what would happen without actually moving files.
        """
        results = []
        for watch_dir in self.watch_dirs:
            if not watch_dir.exists():
                continue
            files = [f for f in watch_dir.iterdir() if f.is_file()]
            logger.info(f"Scanning {len(files)} files in {watch_dir}...")

            classifications = self.classifier.classify_batch(files)
            for cls_result in classifications:
                if cls_result.skip:
                    results.append({"file": cls_result.filepath.name, "action": "skipped"})
                    continue
                if dry_run:
                    results.append({
                        "file": cls_result.filepath.name,
                        "category": cls_result.category,
                        "target": cls_result.target_folder,
                        "suggested_name": cls_result.suggested_name,
                        "method": cls_result.method,
                        "action": "dry_run",
                    })
                else:
                    move_result = self.mover.move(cls_result)
                    results.append({
                        "file": cls_result.filepath.name,
                        "category": cls_result.category,
                        **move_result,
                    })
        return results
