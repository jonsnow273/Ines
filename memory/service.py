"""
Digital Memory Service coordinator.
Runs background screen capture, handles privacy checks, runs OCR,
indexes into vector store, and provides semantic recall endpoints.
"""

import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from core import logger
from core.constants import DATA_DIR, MEMORY_DIR
from memory.privacy import PrivacyGuard
from memory.capture import ScreenCaptureEngine
from memory.ocr import OCREngine
from memory.store import VectorMemoryStore


class DigitalMemoryService:
    """Master manager for Digital Memory screen indexing and recall."""

    def __init__(self, memory_dir: Optional[Path] = None):
        self.memory_dir = memory_dir or MEMORY_DIR
        self.screenshots_dir = self.memory_dir / "screenshots"
        self.vector_dir = self.memory_dir / "vector_store"

        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.vector_dir.mkdir(parents=True, exist_ok=True)

        # Core subsystems
        self.privacy = PrivacyGuard()
        self.capture = ScreenCaptureEngine(
            diff_threshold_percent=self.privacy.config.get("capture", {}).get("diff_threshold_percent", 5.0),
            max_width=self.privacy.config.get("capture", {}).get("max_width", 1280),
            jpeg_quality=self.privacy.config.get("capture", {}).get("jpeg_quality", 75),
        )
        self.ocr = OCREngine()
        self.store = VectorMemoryStore(persist_dir=self.vector_dir)

        # Background thread management
        self.interval = self.privacy.config.get("capture", {}).get("interval_seconds", 5)
        self._running = False
        self._paused_until: Optional[float] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Telemetry stats
        self.total_captures = 0
        self.total_privacy_skips = 0
        self.total_diff_skips = 0
        self.last_capture_time: Optional[str] = None
        self.last_active_app: Optional[str] = None

    @classmethod
    def for_user(cls, username: str) -> "DigitalMemoryService":
        """Factory method to get memory service instance scoped to a specific user account."""
        user_memory_dir = DATA_DIR / "users" / username / "memory"
        return cls(memory_dir=user_memory_dir)

    def start(self) -> bool:
        """Start the background screen capture and memory indexing loop."""
        with self._lock:
            if self._running:
                return True
            self._running = True
            self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="MemoryWorker")
            self._thread.start()
            logger.info("Digital Memory daemon started.")
            return True

    def stop(self) -> bool:
        """Stop the background memory worker."""
        with self._lock:
            if not self._running:
                return True
            self._running = False
            logger.info("Stopping Digital Memory daemon...")
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("Digital Memory daemon stopped.")
        return True

    def pause(self, minutes: int = 15):
        """Temporarily pause memory capture for privacy."""
        self._paused_until = time.time() + (minutes * 60)
        logger.info(f"Digital Memory paused for {minutes} minutes.")

    def resume(self):
        """Resume immediately from pause."""
        self._paused_until = None
        logger.info("Digital Memory resumed from pause.")

    @property
    def is_paused(self) -> bool:
        if self._paused_until is None:
            return False
        if time.time() < self._paused_until:
            return True
        self._paused_until = None
        return False

    @property
    def is_running(self) -> bool:
        return self._running

    def process_frame(self, force: bool = False) -> Dict[str, Any]:
        """
        Processes a single capture cycle:
        1. Privacy check
        2. Diff check
        3. Save optimized JPEG
        4. OCR extraction
        5. Vector indexing
        """
        # 1. Privacy Check
        window_title, process_name = self.privacy.get_active_window_info()
        is_blocked, reason = self.privacy.is_sensitive(window_title, process_name)
        if is_blocked:
            self.total_privacy_skips += 1
            return {"status": "skipped", "reason": f"Privacy: {reason}"}

        # 2. Capture and Diff Check
        saved_path, diff_pct, meta = self.capture.capture_if_changed(
            output_dir=self.screenshots_dir,
            force=force,
        )
        if saved_path is None:
            self.total_diff_skips += 1
            return {"status": "skipped", "reason": f"Diff: {meta.get('reason', 'no change')}", "diff_pct": diff_pct}

        # 3. OCR Text Extraction
        ocr_result = self.ocr.extract_text(saved_path)
        extracted_text = ocr_result.get("text", "")

        # 4. Vector Storage
        memory_id = saved_path.stem
        record_meta = {
            "timestamp": datetime.now().isoformat(),
            "screenshot_path": str(saved_path),
            "window_title": window_title or "Unknown Window",
            "process_name": process_name or "unknown",
            "diff_percent": diff_pct,
            "word_count": ocr_result.get("word_count", 0),
        }

        # Index text content (or window title if text was sparse)
        index_doc = extracted_text if extracted_text else f"App: {process_name} Window: {window_title}"
        self.store.add_memory(
            memory_id=memory_id,
            text=index_doc,
            metadata=record_meta,
        )

        # Update stats
        self.total_captures += 1
        self.last_capture_time = datetime.now().isoformat()
        self.last_active_app = process_name or window_title

        return {
            "status": "captured",
            "memory_id": memory_id,
            "screenshot_path": str(saved_path),
            "window_title": window_title,
            "process_name": process_name,
            "diff_percent": diff_pct,
            "word_count": ocr_result.get("word_count", 0),
            "text_snippet": extracted_text[:120] if extracted_text else "",
        }

    def _worker_loop(self):
        """Continuous background capture loop."""
        while self._running:
            try:
                if not self.is_paused:
                    self.process_frame(force=False)
            except Exception as e:
                logger.error(f"Error in memory worker cycle: {e}")

            # Sleep in short increments to allow rapid shutdown
            for _ in range(max(1, int(self.interval * 2))):
                if not self._running:
                    break
                time.sleep(0.5)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query past digital memory items."""
        return self.store.search(query=query, top_k=top_k)

    def status(self) -> Dict[str, Any]:
        """Telemetry status for dashboard and health checks."""
        return {
            "running": self.is_running,
            "paused": self.is_paused,
            "interval_seconds": self.interval,
            "total_indexed": self.store.count(),
            "total_captures": self.total_captures,
            "total_diff_skips": self.total_diff_skips,
            "total_privacy_skips": self.total_privacy_skips,
            "last_capture_time": self.last_capture_time,
            "last_active_app": self.last_active_app,
            "ocr_available": self.ocr.available,
            "memory_dir": str(self.memory_dir),
        }
