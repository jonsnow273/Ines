"""
Megan Digital Memory package.
Privacy-first on-device screen memory with smart change detection,
OCR text extraction, and semantic vector recall.
"""

from memory.privacy import PrivacyGuard
from memory.capture import ScreenCaptureEngine
from memory.ocr import OCREngine
from memory.store import VectorMemoryStore
from memory.service import DigitalMemoryService

__all__ = [
    "PrivacyGuard",
    "ScreenCaptureEngine",
    "OCREngine",
    "VectorMemoryStore",
    "DigitalMemoryService",
]
