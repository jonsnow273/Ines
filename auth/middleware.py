"""
FastAPI middleware for authentication.
Provides dependency injection functions to protect API routes.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth.models import User, TokenPayload
from auth.service import AuthService

# Bearer token security scheme
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> Optional[User]:
    """
    FastAPI dependency that extracts and validates the Bearer token.
    Returns the User if authenticated, None if no token provided.
    Use this for routes where auth is optional.
    """
    if credentials is None:
        return None

    token_payload = AuthService.verify_token(credentials.credentials)
    if token_payload is None:
        return None

    user = AuthService.get_user_by_username(token_payload.sub)
    return user


async def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> User:
    """
    FastAPI dependency that REQUIRES a valid Bearer token.
    Returns the User if authenticated, raises 401 if not.
    Use this for routes where auth is mandatory.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_payload = AuthService.verify_token(credentials.credentials)
    if token_payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = AuthService.get_user_by_username(token_payload.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or deactivated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
