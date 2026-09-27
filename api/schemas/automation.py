"""Pydantic schemas for automation endpoints."""

from typing import Optional, Any
from pydantic import BaseModel


class ActionRequest(BaseModel):
    category: str
    action: str
    params: Optional[dict] = None


class ActionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    confirmation_required: Optional[bool] = None
    action_description: Optional[str] = None
