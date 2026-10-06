"""
Unit tests for Ines Digital Memory subsystem.
Tests privacy rules, diff detection, image optimization, vector storage,
search queries, and service lifecycle.
"""

import sys
import shutil
import tempfile
import unittest
from pathlib import Path
from PIL import Image

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from memory.privacy import PrivacyGuard
from memory.capture import ScreenCaptureEngine
from memory.ocr import OCREngine
from memory.store import VectorMemoryStore
from memory.service import DigitalMemoryService


class TestDigitalMemory(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_memory_"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_privacy_guard_rules(self):
        """Test privacy guard detects sensitive apps and window titles."""
        guard = PrivacyGuard()

        # Sensitive applications
        self.assertTrue(guard.is_sensitive("Chat", "whatsapp.exe")[0])
        self.assertTrue(guard.is_sensitive("Messages", "telegram.exe")[0])
        self.assertTrue(guard.is_sensitive("Server", "discord.exe")[0])
        self.assertTrue(guard.is_sensitive("Vault", "bitwarden.exe")[0])

        # Sensitive window titles
        self.assertTrue(guard.is_sensitive("WhatsApp Web - Google Chrome", "chrome.exe")[0])
        self.assertTrue(guard.is_sensitive("Private Browsing - Firefox", "firefox.exe")[0])
        self.assertTrue(guard.is_sensitive("Online Banking Portal", "msedge.exe")[0])
        self.assertTrue(guard.is_sensitive("1Password - Unlock", "app.exe")[0])

        # Safe apps
        self.assertFalse(guard.is_sensitive("sephora - Visual Studio Code", "code.exe")[0])
        self.assertFalse(guard.is_sensitive("Administrator: Windows PowerShell", "powershell.exe")[0])
        self.assertFalse(guard.is_sensitive("GitHub - Ines Assistant", "chrome.exe")[0])

    def test_02_image_optimization(self):
        """Test downscaling of high-resolution images."""
        engine = ScreenCaptureEngine(max_width=1280)
        # Create a mock 4K image (3840 x 2160)
        mock_4k = Image.new("RGB", (3840, 2160), color="blue")
        optimized = engine.optimize_image(mock_4k)

        self.assertEqual(optimized.width, 1280)
        self.assertEqual(optimized.height, 720)  # Preserves 16:9 ratio

        # Small image should remain unchanged
        mock_small = Image.new("RGB", (800, 600), color="red")
        optimized_small = engine.optimize_image(mock_small)
        self.assertEqual(optimized_small.width, 800)

    def test_03_diff_calculation(self):
        """Test pixel difference detection between frames."""
        engine = ScreenCaptureEngine(diff_threshold_percent=5.0)

        img1 = Image.new("RGB", (200, 200), color=(100, 100, 100))
        # First frame is 100% diff (initial baseline)
        diff1 = engine.calculate_diff_percent(img1)
        self.assertEqual(diff1, 100.0)

        # Identical second frame should yield ~0% diff
        diff2 = engine.calculate_diff_percent(img1)
        self.assertLess(diff2, 1.0)

        # Drastically different third frame
        img2 = Image.new("RGB", (200, 200), color=(255, 255, 255))
        diff3 = engine.calculate_diff_percent(img2)
        self.assertGreater(diff3, 20.0)

    def test_04_vector_store_indexing_and_search(self):
        """Test vector memory store indexing, search, and count."""
        store_dir = self.temp_dir / "vector_test"
        store = VectorMemoryStore(persist_dir=store_dir)

        # Add records
        store.add_memory(
            memory_id="mem_1",
            text="How to deploy FastAPI with Uvicorn and Gunicorn on Linux server",
            metadata={"process_name": "chrome.exe", "window_title": "FastAPI Deployment Docs"},
        )
        store.add_memory(
            memory_id="mem_2",
            text="Git commit and push changes to remote branch on GitHub",
            metadata={"process_name": "powershell.exe", "window_title": "PowerShell Terminal"},
        )
        store.add_memory(
            memory_id="mem_3",
            text="Python poetry dependency resolution error in pyproject.toml",
            metadata={"process_name": "code.exe", "window_title": "VS Code"},
        )

        self.assertEqual(store.count(), 3)

        # Search for FastAPI
        results = store.search("FastAPI deployment uvicorn", top_k=2)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "mem_1")

        # Search for git
        git_results = store.search("git push remote", top_k=2)
        self.assertGreaterEqual(len(git_results), 1)
        self.assertEqual(git_results[0]["id"], "mem_2")

    def test_05_memory_service_lifecycle(self):
        """Test service start, stop, pause, resume, and status reporting."""
        service = DigitalMemoryService(memory_dir=self.temp_dir)
        self.assertFalse(service.is_running)
        self.assertFalse(service.is_paused)

        # Pause and resume
        service.pause(minutes=10)
        self.assertTrue(service.is_paused)
        service.resume()
        self.assertFalse(service.is_paused)

        # Start and stop
        service.start()
        self.assertTrue(service.is_running)
        status = service.status()
        self.assertTrue(status["running"])

        service.stop()
        self.assertFalse(service.is_running)

    def test_06_user_scoped_service(self):
        """Test creating user-isolated memory services."""
        alice_service = DigitalMemoryService.for_user("alice")
        self.assertIn("alice", str(alice_service.memory_dir))
        self.assertTrue(alice_service.screenshots_dir.exists())
        self.assertTrue(alice_service.vector_dir.exists())


if __name__ == "__main__":
    print("\nRunning Ines Digital Memory Unit Tests...\n")
    unittest.main(verbosity=2)
