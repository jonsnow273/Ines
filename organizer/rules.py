"""
File classification rules for Megan File Organizer.

Provides fast extension-based classification (no LLM needed for obvious types)
and defines the target folder taxonomy.
"""

from pathlib import Path
from typing import Optional

# ── Folder Taxonomy ───────────────────────────────────────────────────────────
# Maps category name → target subfolder name
CATEGORY_FOLDERS = {
    "Documents":    "Documents",
    "Spreadsheets": "Documents/Spreadsheets",
    "Presentations":"Documents/Presentations",
    "PDFs":         "Documents/PDFs",
    "Images":       "Photos",
    "Videos":       "Videos",
    "Audio":        "Music",
    "Code":         "Code",
    "Archives":     "Archives",
    "Installers":   "Installers",
    "Ebooks":       "Ebooks",
    "Fonts":        "Fonts",
    "Data":         "Data",
    "Misc":         "Misc",
}

# ── Extension → Category (fast path, no LLM needed) ──────────────────────────
EXTENSION_MAP = {
    # Documents
    ".doc":  "Documents", ".docx": "Documents", ".odt": "Documents",
    ".rtf":  "Documents", ".txt":  "Documents",
    # Spreadsheets
    ".xls":  "Spreadsheets", ".xlsx": "Spreadsheets",
    ".csv":  "Spreadsheets", ".ods":  "Spreadsheets",
    # Presentations
    ".ppt":  "Presentations", ".pptx": "Presentations",
    ".odp":  "Presentations", ".key":  "Presentations",
    # PDFs
    ".pdf":  "PDFs",
    # Images
    ".jpg":  "Images", ".jpeg": "Images", ".png":  "Images",
    ".gif":  "Images", ".bmp":  "Images", ".tiff": "Images",
    ".webp": "Images", ".svg":  "Images", ".heic": "Images",
    ".raw":  "Images", ".cr2":  "Images",
    # Videos
    ".mp4":  "Videos", ".mkv":  "Videos", ".avi":  "Videos",
    ".mov":  "Videos", ".wmv":  "Videos", ".flv":  "Videos",
    ".webm": "Videos", ".m4v":  "Videos",
    # Audio
    ".mp3":  "Audio", ".wav":  "Audio", ".flac": "Audio",
    ".aac":  "Audio", ".ogg":  "Audio", ".m4a":  "Audio",
    ".wma":  "Audio",
    # Code
    ".py":   "Code", ".js":   "Code", ".ts":   "Code",
    ".jsx":  "Code", ".tsx":  "Code", ".html": "Code",
    ".css":  "Code", ".scss": "Code", ".java": "Code",
    ".cpp":  "Code", ".c":    "Code", ".h":    "Code",
    ".cs":   "Code", ".go":   "Code", ".rs":   "Code",
    ".php":  "Code", ".rb":   "Code", ".sh":   "Code",
    ".json": "Code", ".yaml": "Code", ".yml":  "Code",
    ".toml": "Code", ".xml":  "Code", ".sql":  "Code",
    ".md":   "Code", ".ipynb":"Code",
    # Archives
    ".zip":  "Archives", ".tar":  "Archives", ".gz":  "Archives",
    ".rar":  "Archives", ".7z":   "Archives", ".bz2": "Archives",
    ".xz":   "Archives",
    # Installers
    ".exe":  "Installers", ".msi":  "Installers", ".dmg": "Installers",
    ".deb":  "Installers", ".rpm":  "Installers", ".pkg": "Installers",
    ".appimage": "Installers",
    # Ebooks
    ".epub": "Ebooks", ".mobi": "Ebooks", ".azw":  "Ebooks",
    # Fonts
    ".ttf":  "Fonts", ".otf":  "Fonts", ".woff": "Fonts",
    # Data
    ".db":   "Data", ".sqlite":"Data", ".pkl":  "Data",
    ".parquet": "Data", ".arrow": "Data",
}

# ── Extensions that need LLM for deeper classification ───────────────────────
# (e.g., .txt could be code, notes, or data — LLM decides)
LLM_AMBIGUOUS_EXTENSIONS = {".txt", ".md", ".log", ".csv", ".json", ".xml"}

# ── Extensions/patterns to never touch ───────────────────────────────────────
BLACKLIST_EXTENSIONS = {
    ".lnk", ".tmp", ".temp", ".DS_Store", ".crdownload",
    ".part", ".download", ".lock", ".sys", ".dll",
}

# ── Folder names to never watch or move from ─────────────────────────────────
BLACKLIST_FOLDER_NAMES = {
    "node_modules", ".git", ".venv", "venv", "__pycache__",
    "Megan", "megan", "System32", "Program Files",
}

# ── File patterns to skip (exact names) ──────────────────────────────────────
BLACKLIST_FILENAMES = {
    "desktop.ini", "thumbs.db", ".gitignore", ".env",
    "package-lock.json", "yarn.lock",
}


def classify_by_extension(filepath: Path) -> Optional[str]:
    """
    Fast path: classify a file by its extension alone.
    Returns category name or None if ambiguous/unknown.
    """
    ext = filepath.suffix.lower()
    if ext in BLACKLIST_EXTENSIONS:
        return None  # Skip
    return EXTENSION_MAP.get(ext)


def needs_llm_classification(filepath: Path) -> bool:
    """Return True if LLM is needed for deeper classification."""
    return filepath.suffix.lower() in LLM_AMBIGUOUS_EXTENSIONS


def is_blacklisted(filepath: Path) -> bool:
    """Return True if this file should never be touched."""
    name = filepath.name
    ext = filepath.suffix.lower()
    return (
        ext in BLACKLIST_EXTENSIONS
        or name in BLACKLIST_FILENAMES
        or name.startswith(".")
        or any(part in BLACKLIST_FOLDER_NAMES for part in filepath.parts)
    )


def get_target_folder(category: str) -> str:
    """Return the target subfolder name for a category."""
    return CATEGORY_FOLDERS.get(category, "Misc")
