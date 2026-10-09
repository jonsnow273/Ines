"""
Megan Focus & Anti-Distraction Coach package.
Provides active window monitoring, behavioral focus sessions, distraction nudging,
and one-click workspace restoration.
"""

from focus.tracker import FocusTracker
from focus.coach import FocusCoach

__all__ = ["FocusTracker", "FocusCoach"]
