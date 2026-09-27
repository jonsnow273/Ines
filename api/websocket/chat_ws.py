"""
WebSocket handler for real-time chat streaming.
The frontend connects here for live token-by-token responses.
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core import logger

router = APIRouter()

_engine = None
_steering_engine = None
_context_manager = None


def init(engine, steering_engine, context_manager):
    """Wire up runtime dependencies."""
    global _engine, _steering_engine, _context_manager
    _engine = engine
    _steering_engine = steering_engine
    _context_manager = context_manager


@router.websocket("/ws/chat")
async def chat_websocket(ws: WebSocket):
    """
    WebSocket endpoint for streaming chat.

    Client sends JSON:
        {"message": "...", "session_id": "...", "language": "en"}

    Server streams back JSON frames:
        {"type": "token", "content": "word"}
        {"type": "done", "session_id": "...", "total_tokens": 123}
        {"type": "error", "detail": "..."}
    """
    await ws.accept()
    logger.info("WebSocket chat client connected.")

    from chatbot import new_session, resume_session, load_system_prompt

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)

            message = data.get("message", "")
            session_id = data.get("session_id")
            language = data.get("language", "en")

            if not message:
                await ws.send_json({"type": "error", "detail": "Empty message."})
                continue

            # Session management
            if session_id:
                history = resume_session(session_id)
                if history is None:
                    history = new_session()
            else:
                history = new_session()

            if len(history) == 0:
                history.add_system(load_system_prompt(language))

            history.add("user", message)

            # Trim context
            messages = history.to_llm_format()
            if _context_manager:
                messages = _context_manager.trim(messages)

            # Generate (blocking for now — streaming can be added later)
            try:
                response = await asyncio.to_thread(_engine.generate, messages)

                # Send response as a single frame (for now)
                await ws.send_json({
                    "type": "token",
                    "content": response,
                })

                history.add("assistant", response)

                await ws.send_json({
                    "type": "done",
                    "session_id": history.session_id,
                })

            except Exception as e:
                logger.error(f"WebSocket generation error: {e}")
                await ws.send_json({"type": "error", "detail": str(e)})

    except WebSocketDisconnect:
        logger.info("WebSocket chat client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
