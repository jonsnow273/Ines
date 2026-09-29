"""
Automation REST API routes for Ines.
Handles PC action execution with whitelist validation.
"""

from fastapi import APIRouter, HTTPException

from api.schemas.automation import ActionRequest, ActionResponse
from core import logger

router = APIRouter(prefix="/api/automation", tags=["Automation"])

_action_handler = None


def init(action_handler=None):
    """Wire up automation handler."""
    global _action_handler
    _action_handler = action_handler


@router.post("/execute", response_model=ActionResponse)
async def execute_action(req: ActionRequest):
    """Execute a whitelisted PC action."""
    if _action_handler is None:
        raise HTTPException(status_code=503, detail="Automation handler not initialized.")

    params = req.params or {}

    # Check if action needs confirmation (return confirmation request to frontend)
    if _action_handler.whitelist.is_destructive(req.category, req.action):
        if not _action_handler.whitelist.is_allowed(req.category, req.action):
            return ActionResponse(success=False, message="Action not allowed by whitelist.")
        desc = _action_handler._describe_action(req.category, req.action, **params)
        confirm = _action_handler.confirmation.confirm_api(desc)
        return ActionResponse(
            success=False,
            message=confirm["message"],
            confirmation_required=True,
            action_description=desc,
        )

    result = _action_handler.execute(req.category, req.action, **params)
    return ActionResponse(**result)


@router.post("/confirm")
async def confirm_action(req: ActionRequest):
    """Execute a previously confirmed destructive action (bypasses confirmation)."""
    if _action_handler is None:
        raise HTTPException(status_code=503, detail="Automation handler not initialized.")

    # Temporarily disable confirmation for this call
    old = _action_handler.confirmation.require_confirmation
    _action_handler.confirmation.require_confirmation = False
    try:
        result = _action_handler.execute(req.category, req.action, **(req.params or {}))
    finally:
        _action_handler.confirmation.require_confirmation = old

    return ActionResponse(**result)


@router.get("/whitelist")
async def get_whitelist():
    """Return the current automation whitelist."""
    if _action_handler is None:
        raise HTTPException(status_code=503, detail="Automation handler not initialized.")
    return _action_handler.whitelist.whitelist
