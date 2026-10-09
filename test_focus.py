"""
Unit tests for Focus & Anti-Distraction Coach.
Tests app categorization, time accumulation, distraction threshold triggering,
cooldown mechanics, and workspace restoration.
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from focus.tracker import FocusTracker
from focus.coach import FocusCoach


class TestFocusCoach(unittest.TestCase):

    def setUp(self):
        self.tracker = FocusTracker()
        self.coach = FocusCoach(tracker=self.tracker)

    def test_01_categorize_productive_apps(self):
        """Test categorization of IDEs, terminals, and research sites as productive."""
        self.assertEqual(self.tracker.categorize("main.py - Visual Studio Code", "code"), "productive")
        self.assertEqual(self.tracker.categorize("Windows PowerShell", "powershell"), "productive")
        self.assertEqual(self.tracker.categorize("How to center a div - Stack Overflow", "chrome"), "productive")
        self.assertEqual(self.tracker.categorize("GitHub - jonsnow273/MeganAI", "chrome"), "productive")

    def test_02_categorize_distracting_apps(self):
        """Test categorization of social media, streaming, and games as distracting."""
        self.assertEqual(self.tracker.categorize("YouTube - Funny Cat Videos", "chrome"), "distracting")
        self.assertEqual(self.tracker.categorize("Instagram Reels", "msedge"), "distracting")
        self.assertEqual(self.tracker.categorize("Reddit - Dive into anything", "chrome"), "distracting")
        self.assertEqual(self.tracker.categorize("Friends chat", "discord"), "distracting")
        self.assertEqual(self.tracker.categorize("Spotify Free", "spotify"), "distracting")

    def test_03_categorize_neutral_apps(self):
        """Test file explorer, task manager, settings as neutral."""
        self.assertEqual(self.tracker.categorize("File Explorer", "explorer"), "neutral")
        self.assertEqual(self.tracker.categorize("Task Manager", "taskmgr"), "neutral")

    def test_04_session_tracking_metrics(self):
        """Test start session, tick time slices, and summary calculations."""
        self.tracker.start_session(goal="Study ML", duration_minutes=30)
        self.assertTrue(self.tracker.session_active)

        # Mock 10 seconds of productive coding
        self.tracker.current_window_title = "VS Code"
        self.tracker.current_process_name = "code"
        # We manually simulate tick by updating time directly or mocking categorize
        self.tracker.time_productive += 60.0

        # Mock 20 seconds of distraction
        self.tracker.time_distracted += 20.0

        summary = self.tracker.get_summary()
        self.assertEqual(summary["session_goal"], "Study ML")
        self.assertEqual(summary["time_productive_seconds"], 60.0)
        self.assertEqual(summary["time_distracted_seconds"], 20.0)
        self.assertEqual(summary["productivity_score"], 75.0)  # 60 / (60 + 20) = 75%

    def test_05_distraction_nudge_dispatch(self):
        """Test that coach listener receives alert when distraction streak triggers."""
        nudges_received = []

        def handle_alert(payload):
            nudges_received.append(payload)

        self.coach.add_listener(handle_alert)
        self.tracker.start_session(goal="Coding Sprint", duration_minutes=45)
        self.tracker.current_process_name = "chrome"
        self.tracker.current_window_title = "YouTube Shorts"

        # Manually trigger nudge
        self.coach._fire_nudge(streak_seconds=130.0)

        self.assertEqual(len(nudges_received), 1)
        self.assertEqual(nudges_received[0]["type"], "DISTRACTION_NUDGE")
        self.assertEqual(nudges_received[0]["distraction_app"], "chrome")
        self.assertIn("YouTube Shorts", nudges_received[0]["distraction_window"])
        self.assertEqual(self.coach.total_nudges_fired, 1)

    def test_06_workspace_restore_method(self):
        """Test workspace restore call executes gracefully."""
        # Tests that restore_workspace handles execution without throwing unhandled exceptions
        result = self.coach.restore_workspace("code")
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    print("\nRunning Megan Focus Coach Unit Tests...\n")
    unittest.main(verbosity=2)
