"""
AI File Classifier for Megan.

Classifies files into categories using:
1. Fast path: extension-based rules (instant, no LLM)
2. LLM path: reads file content and asks the local LLM for classification
   (used for ambiguous files like .txt, .md, .csv)
"""

from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from core import logger
from organizer.rules import (
    classify_by_extension,
    needs_llm_classification,
    is_blacklisted,
    get_target_folder,
)

# Max chars to read from file content for LLM classification
MAX_CONTENT_CHARS = 800


@dataclass
class ClassificationResult:
    """Result of classifying a single file."""
    filepath: Path
    category: str
    target_folder: str
    suggested_name: Optional[str] = None
    method: str = "extension"  # "extension" or "llm"
    confidence: float = 1.0
    skip: bool = False
    skip_reason: Optional[str] = None

    @property
    def final_name(self) -> str:
        return self.suggested_name or self.filepath.name


class FileClassifier:
    """
    Classifies files using extension rules + optional LLM.
    Integrates with the project's existing LLM inference engine.
    """

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self._engine = None
        self._llm_available = False
        if use_llm:
            self._try_load_llm()

    def _try_load_llm(self):
        """Try to import and use the existing LLM engine."""
        try:
            from llm import engine, loader
            if loader.is_loaded:
                self._engine = engine
                self._llm_available = True
                logger.info("FileClassifier: LLM engine available.")
            else:
                logger.warning("FileClassifier: LLM not loaded, using extension-only mode.")
        except Exception as e:
            logger.warning(f"FileClassifier: LLM unavailable ({e}), extension-only mode.")

    def classify(self, filepath: Path) -> ClassificationResult:
        """Classify a single file. Returns a ClassificationResult."""
        filepath = Path(filepath)

        # 1. Blacklist check
        if is_blacklisted(filepath):
            return ClassificationResult(
                filepath=filepath,
                category="skip",
                target_folder="",
                skip=True,
                skip_reason="blacklisted file or extension",
            )

        # 2. Extension fast path
        category = classify_by_extension(filepath)
        if category and not needs_llm_classification(filepath):
            return ClassificationResult(
                filepath=filepath,
                category=category,
                target_folder=get_target_folder(category),
                method="extension",
                confidence=0.95,
            )

        # 3. LLM classification for ambiguous files
        if self._llm_available and needs_llm_classification(filepath):
            llm_result = self._classify_with_llm(filepath)
            if llm_result:
                return llm_result

        # 4. Fallback: use extension result or Misc
        final_category = category or "Misc"
        return ClassificationResult(
            filepath=filepath,
            category=final_category,
            target_folder=get_target_folder(final_category),
            method="extension_fallback",
            confidence=0.5,
        )

    def _read_content_snippet(self, filepath: Path) -> str:
        """Read a short snippet of file content for LLM classification."""
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(MAX_CONTENT_CHARS)
        except Exception:
            return ""

    def _classify_with_llm(self, filepath: Path) -> Optional[ClassificationResult]:
        """Use the local LLM to classify ambiguous file types."""
        content_snippet = self._read_content_snippet(filepath)
        filename = filepath.name

        prompt = f"""You are a file organizer. Classify this file and suggest a clean name.

Filename: {filename}
Content preview:
---
{content_snippet[:500]}
---

Respond ONLY with valid JSON in this exact format:
{{
  "category": "<one of: Documents, Code, Data, Misc>",
  "suggested_name": "<clean descriptive filename with same extension>",
  "confidence": <0.0 to 1.0>
}}

Rules:
- If it looks like code or config: category = "Code"
- If it looks like structured data (CSV, JSON with data): category = "Data"
- If it looks like human-written notes or docs: category = "Documents"
- suggested_name must keep the same file extension
- suggested_name should be descriptive and use underscores (no spaces)
"""

        try:
            messages = [
                {"role": "system", "content": "You are a file classification assistant. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ]
            response = self._engine.generate(messages, max_new_tokens=120, temperature=0.1)
            # Extract JSON from response
            match = re.search(r"\{.*?\}", response, re.DOTALL)
            if not match:
                return None
            data = json.loads(match.group())
            category = data.get("category", "Misc")
            suggested_name = data.get("suggested_name", filename)
            confidence = float(data.get("confidence", 0.7))

            # Enforce same extension
            orig_ext = filepath.suffix
            if not suggested_name.endswith(orig_ext):
                suggested_name = Path(suggested_name).stem + orig_ext

            logger.info(f"LLM classified {filename!r} -> {category!r} ({confidence:.0%})")
            return ClassificationResult(
                filepath=filepath,
                category=category,
                target_folder=get_target_folder(category),
                suggested_name=suggested_name,
                method="llm",
                confidence=confidence,
            )
        except Exception as e:
            logger.warning(f"LLM classification failed for {filename!r}: {e}")
            return None

    def classify_batch(self, filepaths: list[Path]) -> list[ClassificationResult]:
        """Classify a list of files."""
        results = []
        for fp in filepaths:
            try:
                results.append(self.classify(fp))
            except Exception as e:
                logger.error(f"Classification error for {fp.name}: {e}")
        return results
