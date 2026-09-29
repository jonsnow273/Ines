"""
Chat REST API routes for Ines.
Handles message sending, session management, and conversation history.
"""

from fastapi import APIRouter, HTTPException

from api.schemas.chat import ChatMessageRequest, ChatMessageResponse, SessionInfo
from core import logger

router = APIRouter(prefix="/api/chat", tags=["Chat"])


# These will be set by server.py at startup
_engine = None
_steering_engine = None
_context_manager = None
_sessions = {}  # session_id -> ConversationHistory


def init(engine, steering_engine, context_manager):
    """Wire up runtime dependencies from server startup."""
    global _engine, _steering_engine, _context_manager
    _engine = engine
    _steering_engine = steering_engine
    _context_manager = context_manager


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(req: ChatMessageRequest):
    """Send a message and get a response."""
    from chatbot import new_session, resume_session, load_system_prompt

    if _engine is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")

    # Get or create session
    session_id = req.session_id
    if session_id and session_id in _sessions:
        history = _sessions[session_id]
    elif session_id:
        history = resume_session(session_id)
        if history is None:
            history = new_session()
        _sessions[history.session_id] = history
    else:
        history = new_session()
        _sessions[history.session_id] = history

    # Inject system prompt if empty session
    if len(history) == 0:
        lang = req.language or "en"
        history.add_system(load_system_prompt(lang))

    # Add user message
    history.add("user", req.message)

    # Trim context if needed
    messages = history.to_llm_format()
    if _context_manager:
        messages = _context_manager.trim(messages)

    # Generate response
    response_text = _engine.generate(messages)
    history.add("assistant", response_text)

    # Get steering status
    steering_info = None
    if _steering_engine:
        status = _steering_engine.status
        if status.get("active"):
            steering_info = status.get("preset")

    logger.info(f"[{history.session_id}] User: {req.message[:50]}... -> {len(response_text)} chars")

    return ChatMessageResponse(
        response=response_text,
        session_id=history.session_id,
        steering_active=steering_info,
    )


@router.get("/sessions")
async def list_sessions():
    """List all saved conversation sessions."""
    from chatbot import list_sessions as ls
    return ls()


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get the full message history for a session."""
    from chatbot import resume_session
    history = resume_session(session_id)
    if history is None:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    return {"session_id": session_id, "messages": history.to_llm_format()}


@router.delete("/history/{session_id}")
async def delete_history(session_id: str):
    """Delete a saved session."""
    from chatbot import delete_session
    if delete_session(session_id):
        _sessions.pop(session_id, None)
        return {"message": f"Session {session_id} deleted."}
    raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
