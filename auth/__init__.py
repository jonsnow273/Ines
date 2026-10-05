"""
Ines Authentication System.
Local user account management with bcrypt password hashing and JWT session tokens.
"""

from auth.database import init_db, get_db
from auth.models import User, UserCreate, UserLogin, TokenPayload
from auth.service import AuthService
from auth.middleware import get_current_user, require_auth

__all__ = [
    "init_db",
    "get_db",
    "User",
    "UserCreate",
    "UserLogin",
    "TokenPayload",
    "AuthService",
    "get_current_user",
    "require_auth",
]
