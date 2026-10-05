"""
Pydantic models for the authentication system.
Defines schemas for user creation, login, token payloads, and database rows.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class UserCreate(BaseModel):
    """Schema for user registration requests."""
    username: str = Field(..., min_length=3, max_length=32, description="Unique username (3-32 chars, alphanumeric + underscores)")
    password: str = Field(..., min_length=6, max_length=128, description="Password (minimum 6 characters)")
    display_name: Optional[str] = Field(None, max_length=64, description="Optional display name")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{2,31}$', v):
            raise ValueError(
                "Username must start with a letter, contain only letters, digits, "
                "and underscores, and be 3-32 characters long."
            )
        return v.lower()


class UserLogin(BaseModel):
    """Schema for login requests."""
    username: str
    password: str


class TokenPayload(BaseModel):
    """JWT token payload (claims)."""
    sub: str           # username
    iat: float         # issued at (unix timestamp)
    exp: float         # expiration (unix timestamp)


class User(BaseModel):
    """Public user representation (never includes password hash)."""
    id: int
    username: str
    display_name: Optional[str] = None
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True


class UserInDB(User):
    """Internal user representation with password hash (never exposed via API)."""
    password_hash: str
