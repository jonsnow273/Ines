"""
Authentication API routes.
Provides REST endpoints for user registration, login, profile, and session management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from auth.models import User, UserCreate, UserLogin
from auth.service import AuthService
from auth.middleware import require_auth, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ── Response Schemas ──────────────────────────────────────────

class RegisterResponse(BaseModel):
    message: str
    user: User


class LoginResponse(BaseModel):
    message: str
    user: User
    token: str


class ProfileResponse(BaseModel):
    user: User


class MessageResponse(BaseModel):
    message: str


# ── Endpoints ─────────────────────────────────────────────────

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate):
    """
    Register a new user account.
    Creates the user in the database and sets up per-user data directories.
    """
    try:
        user = AuthService.register(data)
        return RegisterResponse(
            message=f"Account '{user.username}' created successfully.",
            user=user,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(data: UserLogin):
    """
    Authenticate with username + password and receive a session token.
    Include the token in subsequent requests as: Authorization: Bearer <token>
    """
    try:
        result = AuthService.login(data.username, data.password)
        return LoginResponse(
            message=f"Welcome back, {result['user'].display_name or result['user'].username}!",
            user=result["user"],
            token=result["token"],
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )


@router.get("/me", response_model=ProfileResponse)
async def get_profile(user: User = Depends(require_auth)):
    """
    Get the current authenticated user's profile.
    Requires a valid Bearer token.
    """
    return ProfileResponse(user=user)


@router.post("/logout", response_model=MessageResponse)
async def logout(user: User = Depends(require_auth)):
    """
    Log out the current user.
    Note: Since we use stateless tokens, this is a client-side action.
    The client should discard the token. This endpoint confirms the action.
    """
    return MessageResponse(message=f"User '{user.username}' logged out successfully.")


@router.get("/status")
async def auth_status(user: Optional[User] = Depends(get_current_user)):
    """
    Check if the current request is authenticated.
    Returns the user if logged in, or a guest status if not.
    """
    if user:
        return {
            "authenticated": True,
            "user": user.model_dump(),
        }
    return {
        "authenticated": False,
        "user": None,
    }
