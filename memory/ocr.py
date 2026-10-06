"""
OCR text extraction module for Ines Digital Memory.
Uses Tesseract OCR via pytesseract with auto-detection of Windows installation paths,
text normalization, and graceful degraded mode if Tesseract binary is not present.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from PIL import Image

from core import logger

# Common Windows install locations for Tesseract
WINDOWS_TESSERACT_PATHS = [
    Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
    Path(os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")),
]


class OCREngine:
    """Extracts searchable textual content from screen captures."""

    def __init__(self):
        self.available = False
        self._setup_tesseract()

    def _setup_tesseract(self):
        """Locate tesseract executable and configure pytesseract."""
        try:
            import pytesseract
            self.pytesseract = pytesseract

            # On Windows, check common binary paths if not found on PATH
            if sys.platform == "win32":
                for path in WINDOWS_TESSERACT_PATHS:
                    if path.exists():
                        self.pytesseract.pytesseract.tesseract_cmd = str(path)
                        break

            # Verify availability
            _ = self.pytesseract.get_tesseract_version()
            self.available = True
            logger.info("Tesseract OCR initialized successfully.")
        except Exception as e:
            logger.warning(
                f"Tesseract OCR is not available: {e}. "
                "Digital Memory will operate in visual metadata mode until Tesseract is installed."
            )
            self.available = False

    def extract_text(self, image_path: Path) -> Dict[str, Any]:
        """
        Extract text from an image file.
        Returns: {
            "text": str,
            "word_count": int,
            "lines": list[str],
            "available": bool
        }
        """
        if not self.available:
            return {
                "text": "",
                "word_count": 0,
                "lines": [],
                "available": False,
            }

        try:
            with Image.open(image_path) as img:
                raw_text = self.pytesseract.image_to_string(img)
                lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
                cleaned_text = " ".join(lines)
                words = cleaned_text.split()

                return {
                    "text": cleaned_text,
                    "word_count": len(words),
                    "lines": lines,
                    "available": True,
                }
        except Exception as e:
            logger.error(f"OCR extraction failed for {image_path}: {e}")
            return {
                "text": "",
                "word_count": 0,
                "lines": [],
                "available": False,
                "error": str(e),
            }
