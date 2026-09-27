"""Pydantic schemas for chat endpoints."""

from typing import Optional
from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = None


class ChatMessageResponse(BaseModel):
    response: str
    session_id: str
    tokens_used: Optional[int] = None
    steering_active: Optional[str] = None


class SessionInfo(BaseModel):
    session_id: str
    updated_at: str
    message_count: int
