"""
Focus Coach module for Megan.
Runs background polling, evaluates distraction thresholds, generates proactive
guidance alerts, and provides one-click workspace restoration (minimizing distraction
and refocusing the development environment).
"""

import sys
import time
import threading
from typing import Optional, Dict, Any, Callable, List

from core import logger
from focus.tracker import FocusTracker


class FocusCoach:
    """Orchestrates focus sessions, fires distraction nudges, and restores work context."""

    def __init__(self, tracker: Optional[FocusTracker] = None):
        self.tracker = tracker or FocusTracker()
        self.poll_interval = self.tracker.config.get("focus", {}).get("poll_interval_seconds", 2)
        self.max_distraction_seconds = self.tracker.config.get("focus", {}).get("max_distraction_seconds", 120)
        self.target_app = self.tracker.config.get("focus", {}).get("default_target_app", "code")

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Alert callback list (e.g. WebSocket broadcasters or notification handlers)
        self.alert_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self._last_nudge_time = 0.0
        self.total_nudges_fired = 0

    def add_listener(self, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to real-time distraction and session events."""
        self.alert_listeners.append(callback)

    def start_session(self, goal: str = "Deep Work", duration_minutes: int = 45):
        """Start both tracker metrics and coach background watcher thread."""
        self.tracker.start_session(goal=goal, duration_minutes=duration_minutes)
        with self._lock:
            if not self._running:
                self._running = True
                self._thread = threading.Thread(target=self._watcher_loop, daemon=True, name="FocusCoachWorker")
                self._thread.start()
                logger.info("FocusCoach background monitor started.")

    def stop_session(self) -> Dict[str, Any]:
        """Stop background worker and return final session stats."""
        with self._lock:
            self._running = False
        summary = self.tracker.stop_session()
        summary["total_nudges_fired"] = self.total_nudges_fired
        return summary

    def _watcher_loop(self):
        """Background loop ticking tracker and evaluating distraction boundaries."""
        last_tick = time.time()
        while self._running:
            time.sleep(self.poll_interval)
            now = time.time()
            elapsed = now - last_tick
            last_tick = now

            category, streak = self.tracker.tick(elapsed)

            # Check if distraction threshold exceeded
            if streak >= self.max_distraction_seconds:
                # Cooldown: don't spam nudges more than once every 60 seconds
                if now - self._last_nudge_time > 60.0:
                    self._fire_nudge(streak)
                    self._last_nudge_time = now

    def _fire_nudge(self, streak_seconds: float):
        """Dispatch a distraction warning event to all registered listeners."""
        self.total_nudges_fired += 1
        minutes_wasted = round(streak_seconds / 60.0, 1)
        alert_payload = {
            "type": "DISTRACTION_NUDGE",
            "message": (
                f"You've been on {self.tracker.current_process_name} ({self.tracker.current_window_title[:30]}...) "
                f"for {minutes_wasted} minutes during your focus session."
            ),
            "goal": self.tracker.session_goal,
            "distraction_app": self.tracker.current_process_name,
            "distraction_window": self.tracker.current_window_title,
            "duration_seconds": round(streak_seconds, 1),
            "suggested_action": "restore_workspace",
            "timestamp": time.time(),
        }
        logger.warning(f"Focus Nudge Fired: {alert_payload['message']}")

        for listener in self.alert_listeners:
            try:
                listener(alert_payload)
            except Exception as e:
                logger.error(f"Error in focus alert listener: {e}")

    def restore_workspace(self, target_proc: Optional[str] = None) -> bool:
        """
        One-click workspace restoration:
        Finds and brings the target work window (e.g. VS Code or Terminal) to the foreground.
        Uses native Windows user32 APIs.
        """
        target = (target_proc or self.target_app).lower()

        if sys.platform != "win32":
            logger.info(f"Mock restored workspace: {target}")
            return True

        try:
            import ctypes
            import psutil

            user32 = ctypes.windll.user32
            found_hwnd = None

            # EnumWindows callback to find window belonging to target process
            def enum_windows_callback(hwnd, extra):
                nonlocal found_hwnd
                if user32.IsWindowVisible(hwnd):
                    pid = ctypes.c_ulong()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    try:
                        p = psutil.Process(pid.value)
                        p_name = p.name().lower()
                        if target in p_name:
                            found_hwnd = hwnd
                            return False  # Stop enumeration
                    except Exception:
                        pass
                return True

            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)

            if found_hwnd:
                # Restore if minimized (SW_RESTORE = 9)
                user32.ShowWindow(found_hwnd, 9)
                # Set as active foreground window
                user32.SetForegroundWindow(found_hwnd)
                logger.info(f"Successfully restored workspace window for: '{target}'")
                # Reset distraction streak upon returning to work
                self.tracker.consecutive_distraction_seconds = 0.0
                return True
            else:
                logger.warning(f"No active window found matching target process '{target}'")
                return False
        except Exception as e:
            logger.error(f"Workspace restoration failed: {e}")
            return False

    def status(self) -> Dict[str, Any]:
        """Telemetry status for API and frontend dashboard."""
        summary = self.tracker.get_summary()
        summary["coach_running"] = self._running
        summary["total_nudges_fired"] = self.total_nudges_fired
        summary["max_distraction_seconds"] = self.max_distraction_seconds
        summary["target_app"] = self.target_app
        return summary
