"""
Steering REST API routes for Ines.
Controls activation steering presets, alpha values, and comparison runs.
"""

from fastapi import APIRouter, HTTPException

from api.schemas.steering import (
    SteerRequest, SteerResponse, CompareRequest, CompareResponse, StatusResponse
)
from core import logger

router = APIRouter(prefix="/api/steering", tags=["Steering"])

_steering_engine = None
_engine = None


def init(steering_engine, engine):
    """Wire up runtime dependencies."""
    global _steering_engine, _engine
    _steering_engine = steering_engine
    _engine = engine


@router.post("/set", response_model=SteerResponse)
async def set_steering(req: SteerRequest):
    """Activate a steering preset with given alpha."""
    if _steering_engine is None:
        raise HTTPException(status_code=503, detail="Steering engine not initialized.")

    success = _steering_engine.set_preset(req.preset, alpha=req.alpha)
    status = _steering_engine.status

    return SteerResponse(
        success=success,
        preset=req.preset,
        alpha=req.alpha,
        layer=status.get("layer"),
        message=f"Steering set to '{req.preset}' at alpha={req.alpha}" if success
                else f"Failed to set preset '{req.preset}'",
    )


@router.post("/reset")
async def reset_steering():
    """Reset steering to neutral."""
    if _steering_engine is None:
        raise HTTPException(status_code=503, detail="Steering engine not initialized.")
    _steering_engine.reset()
    return {"message": "Steering reset to neutral."}


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current steering telemetry."""
    if _steering_engine is None:
        raise HTTPException(status_code=503, detail="Steering engine not initialized.")
    s = _steering_engine.status
    return StatusResponse(
        active=s.get("active", False),
        preset=s.get("preset"),
        alpha=s.get("alpha"),
        layer=s.get("layer"),
        vector_norm=s.get("vector_norm"),
    )


@router.post("/compare", response_model=CompareResponse)
async def compare(req: CompareRequest):
    """Run a side-by-side steered vs unsteered comparison."""
    if _steering_engine is None or _engine is None:
        raise HTTPException(status_code=503, detail="Not initialized.")

    messages = [{"role": "user", "content": req.message}]
    result = _steering_engine.compare(messages, preset_name=req.preset, alpha=req.alpha)

    return CompareResponse(
        unsteered=result["unsteered"],
        steered=result["steered"],
        metrics=result["metrics"],
    )


@router.post("/calibrate")
async def calibrate():
    """Calibrate all steering presets."""
    if _steering_engine is None:
        raise HTTPException(status_code=503, detail="Steering engine not initialized.")
    _steering_engine.calibrate()
    return {"message": "Calibration complete.", "cached": list(_steering_engine._direction_cache.keys())}


@router.get("/presets")
async def list_presets():
    """List available steering presets."""
    from steering.presets import PRESETS
    presets = []
    for name, p in PRESETS.items():
        presets.append({
            "name": name,
            "description": p.get("description", ""),
            "default_alpha": p.get("default_alpha", 1.5),
            "target_layer": p.get("target_layer"),
        })
    return presets
