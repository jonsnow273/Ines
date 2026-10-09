"""
Focus Tracker module for Megan.
Monitors active foreground window and process, categorizes time spent into
productive, distracting, or neutral buckets, and calculates live analytics.
"""

import sys
import yaml
import time
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional
from datetime import datetime

from core import logger
from core.constants import CONFIGS_DIR

CONFIG_PATH = CONFIGS_DIR / "focus_rules.yaml"


class FocusTracker:
    """Tracks active window and accumulates time across categories."""

    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self.config = self._load_config()

        # Categorization lists
        self.productive_procs = [p.lower() for p in self.config.get("categories", {}).get("productive", {}).get("processes", [])]
        self.productive_titles = [t.lower() for t in self.config.get("categories", {}).get("productive", {}).get("window_titles", [])]
        self.distracting_procs = [p.lower() for p in self.config.get("categories", {}).get("distracting", {}).get("processes", [])]
        self.distracting_titles = [t.lower() for t in self.config.get("categories", {}).get("distracting", {}).get("window_titles", [])]

        # Live session metrics
        self.session_active = False
        self.session_goal = "General Work"
        self.session_start_time: Optional[float] = None
        self.target_duration_seconds: int = 45 * 60

        # Accumulated seconds
        self.time_productive = 0.0
        self.time_distracted = 0.0
        self.time_neutral = 0.0

        # Current state
        self.current_window_title = ""
        self.current_process_name = ""
        self.current_category = "neutral"
        self.consecutive_distraction_seconds = 0.0

    def _load_config(self) -> Dict[str, Any]:
        """Load YAML configuration or fall back to defaults."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"Error loading focus config: {e}")
        return {}

    def get_active_window_info(self) -> Tuple[str, str]:
        """
        Get current active foreground window title and process name.
        Uses native Windows ctypes for zero CPU overhead.
        """
        if sys.platform != "win32":
            return ("Code Editor", "code")

        try:
            import ctypes
            from ctypes import wintypes
            import psutil

            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return ("", "")

            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            window_title = buf.value

            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            process_name = ""
            if pid.value:
                try:
                    proc = psutil.Process(pid.value)
                    process_name = proc.name().replace(".exe", "")
                except Exception:
                    process_name = ""

            return (window_title, process_name)
        except Exception as e:
            logger.debug(f"Could not inspect active window: {e}")
            return ("", "")

    def categorize(self, window_title: str, process_name: str) -> str:
        """
        Determine category ('productive', 'distracting', or 'neutral').
        Window title keywords take precedence, then process names.
        """
        title_lower = (window_title or "").lower()
        proc_lower = (process_name or "").lower()

        # 1. Check title keywords for distraction (e.g. YouTube in Chrome)
        for d_title in self.distracting_titles:
            if d_title in title_lower:
                return "distracting"

        # 2. Check title keywords for productivity (e.g. GitHub, StackOverflow)
        for p_title in self.productive_titles:
            if p_title in title_lower:
                return "productive"

        # 3. Check process names
        for d_proc in self.distracting_procs:
            if d_proc in proc_lower:
                return "distracting"

        for p_proc in self.productive_procs:
            if p_proc in proc_lower:
                return "productive"

        return "neutral"

    def tick(self, elapsed_seconds: float) -> Tuple[str, float]:
        """
        Update tracking state for an elapsed time slice.
        Returns (category, consecutive_distraction_seconds).
        """
        title, proc = self.get_active_window_info()
        self.current_window_title = title
        self.current_process_name = proc

        category = self.categorize(title, proc)
        self.current_category = category

        if self.session_active:
            if category == "productive":
                self.time_productive += elapsed_seconds
                self.consecutive_distraction_seconds = 0.0
            elif category == "distracting":
                self.time_distracted += elapsed_seconds
                self.consecutive_distraction_seconds += elapsed_seconds
            else:
                self.time_neutral += elapsed_seconds
                # Neutral slowly cools off distraction streak
                self.consecutive_distraction_seconds = max(0.0, self.consecutive_distraction_seconds - (elapsed_seconds * 0.5))

        return (category, self.consecutive_distraction_seconds)

    def start_session(self, goal: str = "Deep Work", duration_minutes: int = 45):
        """Begin a focused work session."""
        self.session_active = True
        self.session_goal = goal
        self.session_start_time = time.time()
        self.target_duration_seconds = duration_minutes * 60
        self.time_productive = 0.0
        self.time_distracted = 0.0
        self.time_neutral = 0.0
        self.consecutive_distraction_seconds = 0.0
        logger.info(f"Focus session started: '{goal}' for {duration_minutes}m")

    def stop_session(self) -> Dict[str, Any]:
        """Stop current session and return final metrics."""
        summary = self.get_summary()
        self.session_active = False
        self.consecutive_distraction_seconds = 0.0
        logger.info(f"Focus session stopped. Score: {summary.get('productivity_score')}%")
        return summary

    def get_summary(self) -> Dict[str, Any]:
        """Calculate productivity statistics and session progress."""
        total_tracked = self.time_productive + self.time_distracted + self.time_neutral
        prod_pct = round((self.time_productive / max(1.0, total_tracked)) * 100.0, 1) if total_tracked > 0 else 100.0
        dist_pct = round((self.time_distracted / max(1.0, total_tracked)) * 100.0, 1) if total_tracked > 0 else 0.0

        elapsed_total = time.time() - self.session_start_time if self.session_start_time else 0.0
        progress_pct = min(100.0, round((elapsed_total / max(1.0, self.target_duration_seconds)) * 100.0, 1))

        return {
            "session_active": self.session_active,
            "session_goal": self.session_goal,
            "target_duration_seconds": self.target_duration_seconds,
            "elapsed_seconds": round(elapsed_total, 1),
            "progress_percent": progress_pct,
            "time_productive_seconds": round(self.time_productive, 1),
            "time_distracted_seconds": round(self.time_distracted, 1),
            "time_neutral_seconds": round(self.time_neutral, 1),
            "productivity_score": prod_pct,
            "distraction_score": dist_pct,
            "current_window": self.current_window_title,
            "current_process": self.current_process_name,
            "current_category": self.current_category,
            "consecutive_distraction_seconds": round(self.consecutive_distraction_seconds, 1),
        }
