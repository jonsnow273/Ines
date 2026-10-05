"""
Authentication service — core business logic.
Handles user registration, login, password hashing, and JWT token management.
"""

import hashlib
import hmac
import json
import os
import time
import base64
from datetime import datetime
from typing import Optional

from core import logger
from auth.database import get_db, ensure_user_data_dir
from auth.models import User, UserCreate, UserInDB, TokenPayload


# JWT-like token settings
# We use HMAC-SHA256 for signing — no external JWT library needed.
TOKEN_EXPIRY_SECONDS = 7 * 24 * 3600  # 7 days
_SECRET_KEY: Optional[str] = None


def _get_secret_key() -> str:
    """
    Get or generate the server secret key for token signing.
    The key is stored in DATA_DIR/auth_secret.key and persists across restarts.
    """
    global _SECRET_KEY
    if _SECRET_KEY is not None:
        return _SECRET_KEY

    from core.constants import DATA_DIR
    key_path = DATA_DIR / "auth_secret.key"

    if key_path.exists():
        _SECRET_KEY = key_path.read_text().strip()
    else:
        _SECRET_KEY = os.urandom(32).hex()
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_text(_SECRET_KEY)
        logger.info("Generated new auth secret key.")

    return _SECRET_KEY


def _hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256 with a random salt.
    Returns a string in the format: salt$hash (both hex-encoded).
    """
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations=100_000)
    return salt.hex() + "$" + pw_hash.hex()


def _verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored salt$hash string."""
    try:
        salt_hex, hash_hex = stored_hash.split("$")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations=100_000)
        return hmac.compare_digest(actual, expected)
    except (ValueError, AttributeError):
        return False


class AuthService:
    """Handles user registration, authentication, and token management."""

    # ── Registration ──────────────────────────────────────────

    @staticmethod
    def register(data: UserCreate) -> User:
        """
        Register a new user account.
        Creates the user in the database and sets up per-user data directories.
        Raises ValueError if username already exists.
        """
        with get_db() as db:
            # Check if username already taken
            existing = db.execute(
                "SELECT id FROM users WHERE username = ?", (data.username,)
            ).fetchone()
            if existing:
                raise ValueError(f"Username '{data.username}' is already taken.")

            # Hash the password
            pw_hash = _hash_password(data.password)
            display = data.display_name or data.username.title()

            # Insert new user
            cursor = db.execute(
                "INSERT INTO users (username, password_hash, display_name) VALUES (?, ?, ?)",
                (data.username, pw_hash, display),
            )
            db.commit()
            user_id = cursor.lastrowid

            # Fetch the created row
            row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

        # Create per-user data directories
        ensure_user_data_dir(data.username)
        logger.info(f"New user registered: {data.username} (id={user_id})")

        return User(
            id=row["id"],
            username=row["username"],
            display_name=row["display_name"],
            created_at=row["created_at"],
            last_login=row["last_login"],
            is_active=bool(row["is_active"]),
        )

    # ── Login ─────────────────────────────────────────────────

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[UserInDB]:
        """
        Validate username + password. Returns the user if valid, None otherwise.
        Also updates the last_login timestamp.
        """
        with get_db() as db:
            row = db.execute(
                "SELECT * FROM users WHERE username = ? AND is_active = 1",
                (username.lower(),),
            ).fetchone()
            if not row:
                return None

            if not _verify_password(password, row["password_hash"]):
                return None

            # Update last_login
            now = datetime.utcnow().isoformat()
            db.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (now, row["id"]),
            )
            db.commit()

            return UserInDB(
                id=row["id"],
                username=row["username"],
                display_name=row["display_name"],
                created_at=row["created_at"],
                last_login=now,
                is_active=bool(row["is_active"]),
                password_hash=row["password_hash"],
            )

    @staticmethod
    def login(username: str, password: str) -> dict:
        """
        Full login flow: authenticate + generate token.
        Returns {"user": User, "token": str} on success.
        Raises ValueError on invalid credentials.
        """
        user = AuthService.authenticate(username, password)
        if user is None:
            raise ValueError("Invalid username or password.")

        token = AuthService.create_token(user.username)
        public_user = User(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            created_at=user.created_at,
            last_login=user.last_login,
            is_active=user.is_active,
        )
        logger.info(f"User logged in: {user.username}")
        return {"user": public_user, "token": token}

    # ── Token Management ──────────────────────────────────────

    @staticmethod
    def create_token(username: str) -> str:
        """
        Create a signed token (HMAC-SHA256 based, JWT-style base64url).
        Format: base64url(payload).base64url(signature)
        """
        now = time.time()
        payload = {
            "sub": username,
            "iat": now,
            "exp": now + TOKEN_EXPIRY_SECONDS,
        }
        payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("ascii").rstrip("=")

        secret = _get_secret_key()
        sig = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).digest()
        sig_b64 = base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=")

        return f"{payload_b64}.{sig_b64}"

    @staticmethod
    def verify_token(token: str) -> Optional[TokenPayload]:
        """
        Verify and decode a token. Returns TokenPayload if valid, None if invalid/expired/tampered.
        """
        try:
            if "." not in token:
                return None
            parts = token.split(".")
            if len(parts) != 2:
                return None
            payload_b64, sig_b64 = parts

            # Restore padding for base64 decode of payload
            pad = len(payload_b64) % 4
            padded_payload_b64 = payload_b64 + ("=" * (4 - pad) if pad else "")
            payload_bytes = base64.urlsafe_b64decode(padded_payload_b64)

            # Re-generate expected signature
            secret = _get_secret_key()
            actual_sig = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).digest()
            actual_sig_b64 = base64.urlsafe_b64encode(actual_sig).decode("ascii").rstrip("=")

            # Constant-time comparison of signatures
            if not hmac.compare_digest(sig_b64, actual_sig_b64):
                return None

            payload = json.loads(payload_bytes.decode("utf-8"))
            if payload.get("exp", 0) < time.time():
                return None

            return TokenPayload(**payload)
        except Exception:
            return None

    # ── User Lookup ───────────────────────────────────────────

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Look up a user by username. Returns None if not found."""
        with get_db() as db:
            row = db.execute(
                "SELECT * FROM users WHERE username = ? AND is_active = 1",
                (username.lower(),),
            ).fetchone()
            if not row:
                return None
            return User(
                id=row["id"],
                username=row["username"],
                display_name=row["display_name"],
                created_at=row["created_at"],
                last_login=row["last_login"],
                is_active=bool(row["is_active"]),
            )

    @staticmethod
    def list_users() -> list[User]:
        """List all active users (admin utility)."""
        with get_db() as db:
            rows = db.execute(
                "SELECT * FROM users WHERE is_active = 1 ORDER BY created_at"
            ).fetchall()
            return [
                User(
                    id=r["id"],
                    username=r["username"],
                    display_name=r["display_name"],
                    created_at=r["created_at"],
                    last_login=r["last_login"],
                    is_active=bool(r["is_active"]),
                )
                for r in rows
            ]

    @staticmethod
    def deactivate_user(username: str) -> bool:
        """Soft-delete a user by setting is_active = 0."""
        with get_db() as db:
            cursor = db.execute(
                "UPDATE users SET is_active = 0 WHERE username = ?",
                (username.lower(),),
            )
            db.commit()
            if cursor.rowcount > 0:
                logger.info(f"User deactivated: {username}")
                return True
            return False
