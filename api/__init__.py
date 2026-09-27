"""
Sephora API — FastAPI backend.

Start the server:
    uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

Endpoints:
    REST  /api/chat/*         Chat message and session management
    REST  /api/steering/*     Activation steering controls
    REST  /api/voice/*        Voice pipeline status
    REST  /api/automation/*   PC action execution
    REST  /api/settings       Application settings
    WS    /ws/chat            Real-time streaming chat
    WS    /ws/voice           Voice audio streaming
    GET   /docs               Interactive Swagger UI
    GET   /health             Health check
"""
