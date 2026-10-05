"""
SQLite database setup for user accounts.
Creates and manages the users.db file under DATA_DIR.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from core import logger
from core.constants import DATA_DIR

# Database path
USERS_DB_PATH = DATA_DIR / "users.db"

# SQL schema for the users table
_CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    display_name  TEXT    DEFAULT NULL,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    last_login    TEXT    DEFAULT NULL,
    is_active     INTEGER NOT NULL DEFAULT 1
);
"""

# Per-user data directory root
USERS_DATA_DIR = DATA_DIR / "users"


def init_db() -> None:
    """Initialize the users database and ensure tables exist."""
    USERS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    USERS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(USERS_DB_PATH))
    try:
        conn.execute(_CREATE_USERS_TABLE)
        conn.commit()
        logger.info(f"Auth database initialized at {USERS_DB_PATH}")
    finally:
        conn.close()


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager that yields a SQLite connection with Row factory enabled."""
    conn = sqlite3.connect(str(USERS_DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def ensure_user_data_dir(username: str) -> Path:
    """
    Create and return the per-user data directory.
    Layout: DATA_DIR/users/<username>/
        ├── memory/         (Digital Memory data)
        ├── organizer/      (File Organizer settings & audit)
        ├── conversations/  (Chat history)
        └── settings/       (User-specific preferences)
    """
    user_dir = USERS_DATA_DIR / username
    subdirs = ["memory", "organizer", "conversations", "settings"]
    for sub in subdirs:
        (user_dir / sub).mkdir(parents=True, exist_ok=True)
    return user_dir
