"""Pydantic schemas for steering endpoints."""

from typing import Optional
from pydantic import BaseModel


class SteerRequest(BaseModel):
    preset: str
    alpha: Optional[float] = 1.5


class SteerResponse(BaseModel):
    success: bool
    preset: str
    alpha: float
    layer: Optional[int] = None
    message: str


class CompareRequest(BaseModel):
    message: str
    preset: str = "concise"
    alpha: float = 1.8


class CompareResponse(BaseModel):
    unsteered: str
    steered: str
    metrics: dict


class StatusResponse(BaseModel):
    active: bool
    preset: Optional[str] = None
    alpha: Optional[float] = None
    layer: Optional[int] = None
    vector_norm: Optional[float] = None
